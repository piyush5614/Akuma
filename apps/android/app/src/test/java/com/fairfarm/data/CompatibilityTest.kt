package com.fairfarm.data

import org.junit.Assert.assertFalse
import org.junit.Test

class CompatibilityTest {
    @Test fun olderAppIsAskedToUpdate() {
        assertFalse(checkCompatibility(Meta("1.0.0", "2.0.0", true), "1.0.0").supported)
    }
}
