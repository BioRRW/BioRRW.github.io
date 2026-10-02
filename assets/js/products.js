// products.js
const productsDatabase = {
    "slim-entryway-console": {
        status: "active",
        title: "The Slim Entryway Console",
        price: "$850",
        basePrice: 850,
        dimensions: "40\" L x 6.75\" D x 30\" H",
        materials: "Solid White Oak & Red Oak, African Mahogany Wedges",
        finish: "Zero-VOC Plant-Based Hardwax Oil",
        description: "Engineered specifically for narrow entryways and hallways without blocking foot traffic. Features hand-fitted through-mortise and tenon joinery wedged with contrasting African Mahogany for a mechanical connection that will never loosen.",
        images: [
            "./assets/images/entryway-table/custom-couch-table.webp",
            "./assets/images/entryway-table/custom-console-table.webp",
            "./assets/images/entryway-table/slim-entryway-table.webp",
            "./assets/images/entryway-table/custom-table-woodworking.mp4",
            "./assets/images/entryway-table/entryway-table-fort-collins-woodworking.mp4",
            "./assets/images/entryway-table/entryway-table-oak-custom.webp",
        ]
    },
    "mountain-modern-trestle": {
        status: "active",
        title: "Mountain Modern X-Frame Trestle",
        price: "Starting at $2,300",
        basePrice: 2300,
        dimensions: "72\" L x 40\" W x 30\" H (Expands to 90\")",
        materials: "Solid Red Oak",
        finish: "Dark Stain with Zero-VOC Hardwax Topcoat",
        description: "A highly structural, clean-lined dining set featuring a precise half-lap X-frame trestle base. Available as a fixed top or an expanding top with an 18-inch leaf. Engineered for real life hosting and finished with non-toxic natural oils.",
        images: [
            "./assets/images/wood/X-table-dark-custom-wood.webp",
            "./assets/images/wood/dining-custom-table-CAD-rendering.webp"
        ],
        // The options array now calculates every permutation based on the $2300 base
        options: [
            { name: "Fixed Table Only (72\")", addedPrice: 0 },
            { name: "Fixed Table + 1 Bench", addedPrice: 750 },
            { name: "Fixed Table + 2 Benches", addedPrice: 1500 },
            { name: "Expanding Table Only (72\" to 90\")", addedPrice: 550 },
            { name: "Expanding Table + 1 Bench", addedPrice: 1300 },
            { name: "Expanding Table + 2 Benches", addedPrice: 2050 }
        ]
    },
    "wedding-arch": {
        status: "sold",
        title: "Handcrafted Wooden Wedding Arch",
        price: "$200",
        dimensions: "Standard Arch Height",
        materials: "Solid Wood",
        finish: "Natural Stain",
        description: "Custom set of wooden wedding arches. Designed to disassemble cleanly for transport and reassembly on site.",
        images: [
            "./assets/images/wood/custom-wedding-arch-wood.webp",
            "./assets/images/wood/custom-wedding-arches-wood.webp"
        ]
    }
};