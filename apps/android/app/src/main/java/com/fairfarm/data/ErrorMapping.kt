package com.fairfarm.data

import retrofit2.HttpException
import java.io.IOException

fun mapApiError(error: Throwable): String = when (error) {
    is IOException -> "Connection unavailable. Check your internet and try again."
    is HttpException -> "The service returned an error (${error.code()}). Please try again."
    else -> error.message ?: "Something went wrong. Please try again."
}
