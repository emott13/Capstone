INSERT INTO vendors(name, email, phone, created_at)

INSERT INTO product_specs ()

INSERT INTO product_colors()

INSERT INTO product_images()

INSERT INTO product_categories(category_name, created_at) 
VALUES
-- ---- SOILS ----
    ('Soils', now()),
    ('Potting Soils', now()),
    ('Garden Soils', now()),
    ('Seed Starting Soils', now()),
    ('Soil Amendments', now()),
    ('Top Soils', now()),



    ('Fertilizers', now()),

    ('Pots', now()),
    ('Planters', now()),
    
    ('Tools', now()),
    ('Garden Tools', now()),
    ('Landscaping Tools', now()),
    
    ('Watering', now()),

    ('Seeds', now()),

    ('Pest Control', now()),

    ('Garden Decor', now()),
    ('Yard Decor', now()),
    ('Outdoor Furniture', now()),
    
    ('Composters', now()),

    ('Indoor Gardening', now()),
    ('Hydroponics', now()),
    ('Grow Lights', now());

INSERT INTO products(vendor_id, name, description, price, created_at) 
VALUES 
    (1, 'Miracle-Gro Potting Mix', 
        'Cultivate a beautiful array of container plants with Miracle-Gro Potting Mix. 
        This potting soil mix Grows Plants Twice As Big!* 
        In addition, the added fertilizer feeds all types of potted plants for up to 6 months. 
        With this gardening soil, you can expect more blooms for more color*. 
        This container mix works best with outdoor container plants, including your favorite flowers, annuals, perennials, vegetables, and shrubs. 
        To apply, select a pot with a drain hole. Fill the pot about 1/3 full with potting soil. 
        Loosen the root ball of your plant and place it in the pot. 
        Add more potting mix and press lightly to level. Water your plant and let it drain. 
        For optimal results, refer to plant tags for specific sun and shade needs. 
        Let mix dry to the touch between waterings; do not allow plants to sit in drainage water. 
        To avoid soil compaction and replenish nutrients, all container plants should be repotted annually or as needed with fresh Miracle-Gro Potting Mix. 
        One 25 qt. bag of Miracle-Gro Potting Mix fills three 10-inch containers. *Vs unfed', 
        15.99, now()),