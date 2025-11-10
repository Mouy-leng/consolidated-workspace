package com.a69v.productionapp;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Test class for ProductionAppApplication
 */
class ProductionAppApplicationTest {
    
    @Test
    void testApplicationRuns() {
        // Test that the application can be instantiated
        ProductionAppApplication app = new ProductionAppApplication();
        assertNotNull(app);
    }
    
    @Test
    void testMainMethod() {
        // Test that main method doesn't throw exceptions
        assertDoesNotThrow(() -> {
            ProductionAppApplication.main(new String[]{});
        });
    }
}
