export const generatorIdMap = {
	0: "00000000-0000-0000-0000-000000000000", // Auto analyze
	1: "01010101-0101-0101-0101-010101010101", // Text to speech (default)
	2: "22222222-2222-2222-2222-222222222222", // Text to image
	3: "33333333-3333-3333-3333-333333333333", // Text to video
	4: "44444444-4444-4444-4444-444444444444", // Text to speech (custom)
	5: "55555555-5555-5555-5555-555555555555", // Enhance image
	6: "66666666-6666-6666-6666-666666666666", // AI - chatbot
	7: "77777777-7777-7777-7777-777777777777", // Answer question
	8: "88888888-8888-8888-8888-888888888888", // Generate code
	9: "99999999-9999-9999-9999-999999999999", // Speech to text
	10: "10101010-1010-1010-1010-101010101010", // Video to text
	11: "11111111-1111-1111-1111-111111111111", // File to text
};

export const reverseGeneratorIdMap = Object.entries(generatorIdMap).reduce(
	(acc, [key, value]) => {
		if (value) acc[value] = key;
		return acc;
	},
	{}
);
