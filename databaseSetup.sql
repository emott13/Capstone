DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS userRoles;
DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS adminDiscounts;
DROP TABLE IF EXISTS vendors;
DROP TABLE IF EXISTS vendorDiscounts;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS phoneNumbers;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS wishlists;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS reviewImages;
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS productSpecifications;
DROP TABLE IF EXISTS productColors;
DROP TABLE IF EXISTS productCategories;
DROP TABLE IF EXISTS productImages;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS orderItems;
DROP TABLE IF EXISTS payments;

-- users -- 
CREATE TABLE IF NOT EXISTS users(
	userID 				BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,					
	username 			VARCHAR(30) UNIQUE NOT NULL,
	fname 				VARCHAR(50) UNIQUE NOT NULL,
	lname 				VARCHAR(50) UNIQUE NOT NULL,
	email				VARCHAR(50) UNIQUE NOT NULL,
	dob					DATE NOT NULL,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP							      -- timestamp of last update
);

-- roles --
CREATE TABLE IF NOT EXISTS roles(
	roleID         		BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,                    -- unique role identifier
    roleName       		VARCHAR(20) UNIQUE NOT NULL,                                        -- name of the role (e.g., admin, vendor, customer)

    created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of role creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP							      -- timestamp of last update
);

-- userRoles (pivot table) --
CREATE TABLE IF NOT EXISTS userRoles(
	userRoleID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	userID				BIGINT NOT NULL REFERENCES users(userID),
	roleID				BIGINT NOT NULL REFERENCES roles(roleID)
)

-- admin and related --
CREATE TABLE IF NOT EXISTS admins(
	adminID				BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update
	
	userID				BIGINT NOT NULL REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS adminDiscounts(
	adminDiscountID		BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	discountPercent		NUMERIC(3, 2),
	
	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	orderID				BIGINT NOT NULL REFERENCES orders(orderID)
);

-- vendors and related --
CREATE TABLE IF NOT EXISTS vendors(
	vendorID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	vendorTitle			VARCHAR(50) NOT NULL,
	
	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	userID				BIGINT NOT NULL REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS vendorDiscounts(
	vendorDiscountID	BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	discountPercent		NUMERIC(3, 2),

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	productID			BIGINT NOT NULL REFERENCES products(productID)
);

-- customers and related --
CREATE TABLE IF NOT EXISTS customers(
	customerID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	userID				BIGINT NOT NULL REFERENCES users(userID)
);

CREATE TABLE IF NOT EXISTS phoneNumbers(
	phoneID				BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	phoneNumber			VARCHAR(15) UNIQUE NOT NULL,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	vendorID			BIGINT NOT NULL REFERENCES vendors(vendorID),
	customerID			BIGINT NOT NULL REFERENCES customers(customerID)
);

CREATE TABLE IF NOT EXISTS addresses(
	addressID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	address1			VARCHAR(50) UNIQUE NOT NULL,
	address2			VARCHAR(50) UNIQUE NOT NULL,
	city				VARCHAR(50) UNIQUE NOT NULL,
	state				VARCHAR(50) UNIQUE NOT NULL,
	country				VARCHAR(50) UNIQUE NOT NULL,
	postalCode			VARCHAR(20) UNIQUE NOT NULL,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	orderID				BIGINT REFERENCES orders(orderID),
	customerID			BIGINT REFERENCES customers(customerID)

	-- set constraint so one has to be filled
);

CREATE TABLE IF NOT EXISTS carts(
	cartID				BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	customerID			BIGINT NOT NULL REFERENCES customers(customerID),
	productID			BIGINT NOT NULL REFERENCES products(productID)
);

CREATE TABLE IF NOT EXISTS wishlists(
	wishlistID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	wishlistTitle		VARCHAR(50) UNIQUE NOT NULL,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	customerID			BIGINT NOT NULL REFERENCES customers(customerID),
	productID			BIGINT NOT NULL REFERENCES products(productID)
);

CREATE TABLE IF NOT EXISTS reviews(
	reviewID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	title				VARCHAR(50) UNIQUE NOT NULL,
	description			VARCHAR(255) UNIQUE NOT NULL,
	rating				INT UNIQUE NOT NULL,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	customerID			BIGINT NOT NULL REFERENCES customers(customerID)
);

CREATE TABLE IF NOT EXISTS reviewImages(
	imageID				BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	imageLink			TEXT,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	reviewID			BIGINT NOT NULL REFERENCES reviews(reviewID)
);

CREATE TABLE IF NOT EXISTS complaints(
	complaintID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	title				VARCHAR(30),
	description			VARCHAR(255),

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	orderID				BIGINT NOT NULL REFERENCES orders(orderID)
);

-- products and related --
CREATE TABLE IF NOT EXISTS products(
	productID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	name				VARCHAR(50),
	description			TEXT,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	vendorID			BIGINT NOT NULL REFERENCES vendors(vendorID)
);

CREATE TABLE IF NOT EXISTS productSpecifications(
	productSpecID		BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	specification		VARCHAR(255),

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	productID			BIGINT NOT NULL REFERENCES products(productID)
);

CREATE TABLE IF NOT EXISTS productColors(
	productColorID		BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	colorCode			BIGINT NOT NULL,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	productID			BIGINT NOT NULL REFERENCES products(productID)
);

CREATE TABLE IF NOT EXISTS productCategories(
	productCategoryID	BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	name				VARCHAR(50),
	description			VARCHAR(255),

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	productID			BIGINT NOT NULL REFERENCES products(productID)
);

CREATE TABLE IF NOT EXISTS productImages(
	imageID				BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	imageLink			TEXT,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	productID			BIGINT NOT NULL REFERENCES products(productID)
);

-- orders and related --
CREATE TABLE IF NOT EXISTS orders(
	orderID				BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	orderDateTime		TIMESTAMP WITH TIMEZONE
	orderTotal			NUMERIC(12, 2) NOT NULL
	orderStatus			VARCHAR(20), -- pending, received, shipped, etc?

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP							      -- timestamp of last update
);

CREATE TABLE IF NOT EXISTS orderItems(
	orderItemID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update
	
	orderID				BIGINT NOT NULL REFERENCES orders(orderID),
	productID			BIGINT NOT NULL REFERENCES products(productID)
);

CREATE TABLE IF NOT EXISTS payments(
	paymentID			BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	amount				NUMERIC(12, 2) NOT NULL,

	created_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                                -- timestamp of creation
    updated_at      	TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,							      -- timestamp of last update

	orderID				BIGINT NOT NULL REFERENCES orders(orderID)
);
