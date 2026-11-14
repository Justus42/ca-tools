#!/usr/bin/env Rscript
## powercz.R - build a Power CZ array from its certificate, in R.
##
## Reads a construction certificate of the kind "powercz-1" with a Reed-Solomon hash family
## (table/constructions/, format in tools/CONSTRUCTION_CERT.md) and returns the covering array as an
## integer matrix with symbols 0..v-1. It follows the recipe only: it does not check the hypotheses of
## the coverage proof. tools/construction_cert.py does that, and CAs::coverage() checks a small array
## directly. Needs the package jsonlite; with the package digest it also compares the sha256 of the
## array's canonical text with the one the certificate records.
##
## In R:      source("tools/powercz.R"); A <- powercz("table/constructions/powercz/CA_216_4_1368_2.cert.json")
## In a shell: Rscript tools/powercz.R CERT.json [OUT.txt]
##
## The recipe (Colbourn and Zhou 2012, Theorem 2.2 with Lemma 2.3):
##   1. The columns are the polynomials c_0 + c_1 x + ... + c_(e-1) x^(e-1) over GF(q), in
##      lexicographic order of (c_0, ..., c_(e-1)) with c_0 most significant.
##   2. Every row of the family has an evaluation point (a field element, or "inf" for the
##      coefficient c_(e-1)). Its value in a column is the polynomial evaluated at the point.
##   3. A row may have forbidden values. A column taking a forbidden value in any row is deleted.
##      The values left in that row are renumbered 0, 1, ... in increasing order; their number is
##      the width of the row. column_limit, if present, keeps only the first so many columns.
##   4. Every row has an ingredient: an array over 0..v-1 with as many columns as the row's width.
##      Block i of the result is the ingredient with its column h placed in every column of the
##      result whose value in row i is h. The blocks are stacked in the order of the rows.

gf_tables <- function(q, p, m, modulus) {
  ## elements are 0..q-1; the base-p digits of an element, least significant first, are the
  ## coefficients of a polynomial modulo the monic modulus (coefficients constant term first)
  digits <- function(a) { d <- integer(m); for (i in seq_len(m)) { d[i] <- a %% p; a <- a %/% p }; d }
  number <- function(d) sum(d * p^(seq_len(m) - 1))
  D <- t(vapply(0:(q - 1), digits, integer(m))); if (m == 1) D <- matrix(D, ncol = 1)
  add <- matrix(0L, q, q); mul <- matrix(0L, q, q)
  for (a in 0:(q - 1)) for (b in 0:(q - 1)) {
    add[a + 1, b + 1] <- as.integer(number((D[a + 1, ] + D[b + 1, ]) %% p))
    if (m == 1) { mul[a + 1, b + 1] <- as.integer((a * b) %% p); next }
    prod <- integer(2 * m - 1)
    for (i in seq_len(m)) for (j in seq_len(m))
      prod[i + j - 1] <- (prod[i + j - 1] + D[a + 1, i] * D[b + 1, j]) %% p
    for (d in (2 * m - 1):(m + 1)) {                 # reduce: x^m = -(modulus without its leading term)
      cf <- prod[d]; if (cf == 0) next
      prod[d] <- 0L
      prod[(d - m):(d - 1)] <- (prod[(d - m):(d - 1)] - cf * modulus[seq_len(m)]) %% p
    }
    mul[a + 1, b + 1] <- as.integer(number(prod[seq_len(m)]))
  }
  list(add = add, mul = mul)
}

powercz <- function(cert_file, check_hash = TRUE) {
  if (!requireNamespace("jsonlite", quietly = TRUE)) stop("the package jsonlite is needed")
  cert <- jsonlite::fromJSON(cert_file, simplifyVector = FALSE)
  if (!identical(cert$construction, "powercz-1")) stop("not a powercz-1 certificate")
  fam <- cert$family
  if (!identical(fam$type, "reed-solomon")) stop("only the Reed-Solomon family is built here")
  e <- cert$e; v <- cert$v
  q <- cert$field$q; p <- cert$field$p; m <- if (is.null(cert$field$m)) 1L else cert$field$m
  modulus <- if (m > 1) unlist(cert$field$modulus) else c(0L, 1L)
  gf <- gf_tables(q, p, m, modulus)
  ## step 1: all coefficient tuples, c_0 most significant
  cols <- as.matrix(expand.grid(rep(list(0:(q - 1)), e)))[, e:1, drop = FALSE]
  ## step 2: the value of every row of the family in every column
  M <- length(fam$rows)
  H <- matrix(0L, M, nrow(cols))
  for (i in seq_len(M)) {
    pt <- fam$rows[[i]]$point
    if (identical(pt, "inf")) { H[i, ] <- cols[, e]; next }
    val <- cols[, e]                                 # Horner: ((c_(e-1)) x + c_(e-2)) x + ...
    if (e > 1) for (j in (e - 1):1) val <- gf$add[cbind(gf$mul[cbind(val + 1, pt + 1)] + 1, cols[, j] + 1)]
    H[i, ] <- val
  }
  ## step 3: delete the columns with a forbidden value, renumber the values of each row
  keep <- rep(TRUE, ncol(H))
  for (i in seq_len(M)) keep <- keep & !(H[i, ] %in% unlist(fam$rows[[i]]$forbidden))
  H <- H[, keep, drop = FALSE]
  for (i in seq_len(M)) {
    left <- setdiff(0:(q - 1), unlist(fam$rows[[i]]$forbidden))
    H[i, ] <- match(H[i, ], left) - 1L
  }
  if (!is.null(fam$column_limit)) H <- H[, seq_len(fam$column_limit), drop = FALSE]
  ## step 4: one block per row
  dir <- dirname(cert_file)
  ingredient <- function(name) {
    g <- cert$ingredients[[name]]
    if (!is.null(g$file)) return(unname(as.matrix(utils::read.table(file.path(dir, g$file)))))
    if (!is.null(g$rows)) return(do.call(rbind, lapply(g$rows, unlist)))
    stop("ingredient ", name, " is an array of the table (sha256 ", g$table,
         "); fetch it from table/arrays and put it in the certificate's folder")
  }
  A <- do.call(rbind, lapply(seq_len(M), function(i) {
    Q <- ingredient(fam$rows[[i]]$ingredient)
    Q[, H[i, ] + 1, drop = FALSE]
  }))
  storage.mode(A) <- "integer"
  stopifnot(nrow(A) == cert$expected$N, ncol(A) == cert$expected$k)
  if (check_hash && requireNamespace("digest", quietly = TRUE)) {
    txt <- paste0(paste(apply(A, 1, paste, collapse = " "), collapse = "\n"), "\n")
    got <- digest::digest(txt, algo = "sha256", serialize = FALSE)
    if (!identical(got, cert$expected$array_sha256))
      stop("the array built here does not have the sha256 the certificate records")
    attr(A, "sha256") <- got
  }
  A
}

if (sys.nframe() == 0 && !interactive()) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) < 1) stop("usage: Rscript tools/powercz.R CERT.json [OUT.txt]")
  A <- powercz(args[1])
  cat(sprintf("CA(%d; %d columns) built%s\n", nrow(A), ncol(A),
              if (is.null(attr(A, "sha256"))) "" else paste0(", sha256 ", attr(A, "sha256"), " as recorded")))
  if (length(args) > 1) utils::write.table(A, args[2], row.names = FALSE, col.names = FALSE)
}
