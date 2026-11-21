package com.fairfarm.data

data class Compatibility(val supported: Boolean, val message: String? = null)

fun checkCompatibility(meta: Meta, installedVersion: String): Compatibility {
    return if (installedVersion < meta.min_app_version) {
        Compatibility(false, "Please update FairFarm to continue.")
    } else {
        Compatibility(true)
    }
}
