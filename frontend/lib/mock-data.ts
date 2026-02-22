export const mockDashboardStats = {
  totalOrders: 1247,
  totalRevenue: 487392,
  tyresInStock: 12456,
  carModels: 89,
};

export const mockOrders = [
  {
    id: 'ORD-001',
    customerName: 'John Smith',
    status: 'Delivered',
    date: '2024-02-15',
    amount: 1250,
    items: 4,
    details: {
      items: ['Michelin Pilot Sport 225/45R17', 'Bridgestone Turanza 225/45R17', 'Goodyear Assurance 205/55R16', 'Continental EcoContact 205/55R16'],
      shippingAddress: '123 Main St, New York, NY 10001',
      paymentMethod: 'Credit Card',
    },
  },
  {
    id: 'ORD-002',
    customerName: 'Sarah Johnson',
    status: 'Processing',
    date: '2024-02-18',
    amount: 890,
    items: 2,
    details: {
      items: ['Pirelli P Zero 235/40R19', 'Pirelli P Zero 235/40R19'],
      shippingAddress: '456 Oak Ave, Los Angeles, CA 90001',
      paymentMethod: 'Debit Card',
    },
  },
  {
    id: 'ORD-003',
    customerName: 'Mike Davis',
    status: 'Pending',
    date: '2024-02-20',
    amount: 2100,
    items: 8,
    details: {
      items: ['Dunlop SP Sport 255/35R18', 'Kumho Solus 185/65R15', 'Hankook Kinergy 215/60R16', 'Falken Ziex 195/55R15', 'Toyo Proxes 215/50R17', 'Cooper CS5 205/60R16', 'General Altimax 225/60R17', 'Vredestein Sportrac 175/70R14'],
      shippingAddress: '789 Pine Rd, Chicago, IL 60601',
      paymentMethod: 'Bank Transfer',
    },
  },
  {
    id: 'ORD-004',
    customerName: 'Emily Brown',
    status: 'Delivered',
    date: '2024-02-12',
    amount: 1550,
    items: 4,
    details: {
      items: ['Michelin LTX M/S2 P275/60R20', 'Bridgestone Dueler H/P 275/60R20', 'Continental DWS Plus 275/60R20', 'Goodyear Assurance MaxLife 275/60R20'],
      shippingAddress: '321 Elm St, Houston, TX 77001',
      paymentMethod: 'Credit Card',
    },
  },
  {
    id: 'ORD-005',
    customerName: 'Robert Wilson',
    status: 'Cancelled',
    date: '2024-02-10',
    amount: 670,
    items: 2,
    details: {
      items: ['Pirelli Scorpion Verde 235/55R19', 'Pirelli Scorpion Verde 235/55R19'],
      shippingAddress: '654 Maple Dr, Phoenix, AZ 85001',
      paymentMethod: 'PayPal',
    },
  },
];

export const mockCarBrands = [
  { id: 1, name: 'Toyota', country: 'Japan', models: 12 },
  { id: 2, name: 'Honda', country: 'Japan', models: 10 },
  { id: 3, name: 'BMW', country: 'Germany', models: 15 },
  { id: 4, name: 'Mercedes-Benz', country: 'Germany', models: 18 },
  { id: 5, name: 'Ford', country: 'USA', models: 11 },
  { id: 6, name: 'Chevrolet', country: 'USA', models: 9 },
  { id: 7, name: 'Volkswagen', country: 'Germany', models: 14 },
  { id: 8, name: 'Audi', country: 'Germany', models: 13 },
];

export const mockCarModels = [
  { id: 1, brand: 'Toyota', model: 'Camry', year: 2024, tyreSizes: ['225/45R17', '225/55R17'], segmentCount: 5 },
  { id: 2, brand: 'Toyota', model: 'Corolla', year: 2024, tyreSizes: ['205/55R16', '215/55R16'], segmentCount: 3 },
  { id: 3, brand: 'Honda', model: 'Accord', year: 2024, tyreSizes: ['225/45R17', '225/55R17'], segmentCount: 4 },
  { id: 4, brand: 'Honda', model: 'Civic', year: 2024, tyreSizes: ['205/55R16', '215/50R17'], segmentCount: 3 },
  { id: 5, brand: 'BMW', model: '320i', year: 2024, tyreSizes: ['225/50R17', '225/45R18'], segmentCount: 5 },
  { id: 6, brand: 'BMW', model: '530i', year: 2024, tyreSizes: ['235/50R18', '245/45R19'], segmentCount: 6 },
  { id: 7, brand: 'Mercedes-Benz', model: 'C-Class', year: 2024, tyreSizes: ['225/45R17', '225/40R18'], segmentCount: 5 },
  { id: 8, brand: 'Mercedes-Benz', model: 'E-Class', year: 2024, tyreSizes: ['235/50R18', '245/45R19'], segmentCount: 6 },
  { id: 9, brand: 'Ford', model: 'F-150', year: 2024, tyreSizes: ['265/70R17', '275/60R20'], segmentCount: 4 },
  { id: 10, brand: 'Chevrolet', model: 'Silverado', year: 2024, tyreSizes: ['265/70R17', '275/65R18'], segmentCount: 4 },
];

export const mockTyreBrands = [
  { id: 1, name: 'Michelin', country: 'France', typesCount: 24 },
  { id: 2, name: 'Bridgestone', country: 'Japan', typesCount: 22 },
  { id: 3, name: 'Continental', country: 'Germany', typesCount: 21 },
  { id: 4, name: 'Goodyear', country: 'USA', typesCount: 20 },
  { id: 5, name: 'Pirelli', country: 'Italy', typesCount: 19 },
  { id: 6, name: 'Dunlop', country: 'UK', typesCount: 18 },
  { id: 7, name: 'Hankook', country: 'South Korea', typesCount: 17 },
  { id: 8, name: 'Kumho', country: 'South Korea', typesCount: 16 },
];

export const mockTyres = [
  { id: 1, brand: 'Michelin', model: 'Pilot Sport 4', size: '225/45R17', type: 'Performance', price: 189.99, cost: 95.50, stock: 156 },
  { id: 2, brand: 'Bridgestone', model: 'Turanza T005', size: '225/45R17', type: 'Comfort', price: 165.99, cost: 82.75, stock: 243 },
  { id: 3, brand: 'Continental', model: 'EcoContact 6', size: '205/55R16', type: 'Eco', price: 129.99, cost: 65.00, stock: 318 },
  { id: 4, brand: 'Goodyear', model: 'Assurance MaxLife', size: '225/60R17', type: 'All-Season', price: 145.99, cost: 73.00, stock: 287 },
  { id: 5, brand: 'Pirelli', model: 'P Zero', size: '235/40R19', type: 'Performance', price: 249.99, cost: 125.00, stock: 89 },
  { id: 6, brand: 'Dunlop', model: 'SP Sport Maxx', size: '255/35R18', type: 'Performance', price: 219.99, cost: 110.00, stock: 102 },
  { id: 7, brand: 'Hankook', model: 'Kinergy', size: '215/60R16', type: 'All-Season', price: 119.99, cost: 60.00, stock: 401 },
  { id: 8, brand: 'Kumho', model: 'Solus', size: '185/65R15', type: 'Comfort', price: 109.99, cost: 55.00, stock: 523 },
];

export const mockStockItems = [
  { id: 1, tyreBrand: 'Michelin', model: 'Pilot Sport 4', size: '225/45R17', currentStock: 156, minLevel: 100, status: 'OK', lastUpdate: '2024-02-18' },
  { id: 2, tyreBrand: 'Bridgestone', model: 'Turanza T005', size: '225/45R17', currentStock: 243, minLevel: 150, status: 'OK', lastUpdate: '2024-02-17' },
  { id: 3, tyreBrand: 'Continental', model: 'EcoContact 6', size: '205/55R16', currentStock: 42, minLevel: 100, status: 'Low', lastUpdate: '2024-02-19' },
  { id: 4, tyreBrand: 'Goodyear', model: 'Assurance MaxLife', size: '225/60R17', currentStock: 287, minLevel: 150, status: 'OK', lastUpdate: '2024-02-16' },
  { id: 5, tyreBrand: 'Pirelli', model: 'P Zero', size: '235/40R19', currentStock: 15, minLevel: 50, status: 'Critical', lastUpdate: '2024-02-19' },
];

export const mockChatMessages = [
  { id: 1, sender: 'agent', text: 'Hello! How can I help you today?', timestamp: '10:30 AM' },
  { id: 2, sender: 'user', text: 'Hi, I need to check the stock for Michelin tires', timestamp: '10:31 AM' },
  { id: 3, sender: 'agent', text: 'Sure! I can help you with that. Which specific model and size are you looking for?', timestamp: '10:32 AM' },
  { id: 4, sender: 'user', text: 'Michelin Pilot Sport 4 in 225/45R17', timestamp: '10:33 AM' },
  { id: 5, sender: 'agent', text: 'Great! We currently have 156 units of Michelin Pilot Sport 4 in size 225/45R17 in stock.', timestamp: '10:34 AM' },
];
