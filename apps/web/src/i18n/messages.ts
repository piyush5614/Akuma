import type { Language } from "../api/client";

export const messages: Record<Language, Record<string, string>> = {
  en: { overview: "Overview", explorer: "Price Explorer", regions: "Regions", insights: "Insights", data: "Data", settings: "Settings", queries: "Query log", saathi: "Saathi", title: "More in your pocket.", subtitle: "Compare what each mandi leaves you after costs.", loading: "Loading…", retry: "Try again", demo: "DEMO DATA", noData: "No data available yet." },
  mr: { overview: "आढावा", explorer: "भाव शोधक", regions: "प्रदेश", insights: "अंतर्दृष्टी", data: "डेटा", settings: "सेटिंग्ज", queries: "क्वेरी लॉग", saathi: "साथी", title: "तुमच्या खिशात अधिक.", subtitle: "खर्चानंतर प्रत्येक मंडी किती देते ते पहा.", loading: "लोड होत आहे…", retry: "पुन्हा प्रयत्न", demo: "डेमो डेटा", noData: "अजून डेटा उपलब्ध नाही." },
  hi: { overview: "अवलोकन", explorer: "भाव खोजक", regions: "क्षेत्र", insights: "अंतर्दृष्टि", data: "डेटा", settings: "सेटिंग्स", queries: "क्वेरी लॉग", saathi: "साथी", title: "आपकी जेब में अधिक.", subtitle: "खर्च के बाद हर मंडी कितना देती है देखें.", loading: "लोड हो रहा है…", retry: "फिर प्रयास करें", demo: "DEMO DATA", noData: "अभी डेटा उपलब्ध नहीं है." },
};
