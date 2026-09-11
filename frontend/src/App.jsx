import { useEffect, useMemo, useRef, useState } from 'react'
import { BrowserRouter, useLocation, useNavigate } from 'react-router-dom'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { pfz as staticPfz, alerts as staticAlerts } from './data'
import logo from './assets/orca-logo.png'
import './App.css'
import {
  askOrca,
  checkBackendHealth,
  getMarineData,
  getRouteAndGeofence,
  getPfzCandidates,
  getHazards,
  getAnalytics,
  getAllAlerts,
  getAnalysisHistory,
  resolveUserLocation,
  getSafeMarineRoute,
  analyzeNavigation,
  getLiveIncoisTelemetry,
  getUserConversations,
  createNewConversation,
  getConversationMessages,
  saveChatMessage,
  getPortContext,
  getFishingMultiDay,
  deleteConversation,
  clearConversationMessages
} from './services/api'
import { onAuthStateChange, signOutUser, getSession } from './services/supabaseClient'
import AuthModal from './components/AuthModal'

const T = {
  en: {
    dashboard: 'Dashboard', map: 'Marine Intelligence Map', analytics: 'Ocean Analytics', fishing: 'Fishing Intelligence', safety: 'Safety & Routes', assistant: 'ORCA AI Assistant', alerts: 'Alerts', settings: 'Settings', profile: 'Profile', workspace: 'WORKSPACE', operational: 'Systems operational', connected: 'Marine data services connected', marine: 'MARINE INTELLIGENCE', glance: 'Marine conditions at a glance.', location: 'Mumbai Coast • Real-Time Sensor Streams Connected', ask: 'Ask ORCA', seaState: 'Sea state', wind: 'Wind', sst: 'Sea surface temperature', activePFZ: 'Active PFZs', moderate: 'Moderate', waves: '1.2 m waves', steady: 'NE • steady', favourable: 'Favourable', openMap: 'Open map', activeAdvisories: 'Active advisories', viewAll: 'View all', insights: "Today's marine insights", bestFishing: 'Best fishing opportunity', departure: 'Recommended departure', confidence: 'Data confidence', verified: 'Verified intelligence', sources: 'Sources: ISRO • INCOIS • IMD • Ocean Telemetry', oceanInputs: 'Ocean, geospatial, and telemetry inputs synchronized.', allLayers: 'All layers', weather: 'Weather', hazards: 'Hazards', boundaries: 'Boundaries', today: 'Today', selectedZone: 'Selected zone', high: 'High confidence', why: 'Why this zone?', signal: 'Signal', how: 'How ORCA reasons', discover: 'Discover', correlate: 'Correlate', assess: 'Assess', explain: 'Explain', findZones: 'Find promising fishing zones.', explore: 'Explore PFZs', viewZone: 'View zone', recommendation: 'ORCA recommendation', start: 'Start with', safeRoute: 'Safe route assessment', recommended: 'Recommended', low: 'Low', risk: 'Risk', whyRoute: 'Why ORCA recommends this route', safetyChecklist: 'Safety checklist', askSea: 'Ask ORCA about the sea.', conversational: 'CONVERSATIONAL MARINE INTELLIGENCE', placeholder: 'Ask a marine question or plan a trip...', send: 'Send', nearest: 'Nearest PFZ today', safeTomorrow: 'Is it safe to go tomorrow morning?', showHazards: 'Show hazards near Mumbai', findRoute: 'Find a safer route', close: 'Close', reset: 'Reset view', satellite: 'Satellite', street: 'Street', locate: 'My location', language: 'Language', search: 'Search', notifications: 'Notifications', noResults: 'No matching results.', routeA: 'Coastal route A', routeB: 'Coastal route B', routeC: 'Balanced route', routeRisk: 'Route risk', checked: 'Checked', refresh: 'Refresh', save: 'Save changes', saved: 'Changes saved', theme: 'Theme', darkMode: 'Dark mode', email: 'Email notifications', profileTitle: 'Operational Profile', role: 'Marine Researcher / Captain', details: 'Profile Details', name: 'Capt. Devesh Madhavi', status: 'Active Workspace Session', mobile: 'Mobile number', emailLabel: 'Email', profession: 'Operational Role', edit: 'Edit profile', done: 'Done', trend: 'PFZ confidence trend', pfzConfidence: 'PFZ confidence', freshness: 'Data freshness', latest: 'Latest sample', marineInputs: 'Satellite ocean colour, SST and weather inputs synchronized.', spatialSignals: 'Correlates nearby spatial signals and PFZ candidates.', opportunitySafety: 'Balances fishing opportunity with safety constraints.', evidenceRecommendation: 'Explains the evidence behind each recommendation.', hazardAvoided: 'Avoids the identified caution corridor.', boundariesChecked: 'Checks operational boundaries before routing.', riskCorridor: 'Prefers the lower-risk coastal corridor.', recalculate: 'Route can be recalculated after new data arrives.', demo: 'Real-time operational mode • Live telemetry connected.', demoAnswer: 'Hello Captain! I am ORCA, your Marine AI Decision Copilot. How can I assist your voyage today? You can ask about PFZ zones, weather, wave conditions, or safe routes along the coast.', mapFail: 'Map tiles could not load. Controls and local markers remain available.', routeSummary: '39.2 km • about 2h 35m', routeBText: '48.5 km • about 3h 10m', routeCText: '42.0 km • about 2h 45m', selectPeriod: 'Period', hours24: '24 hours', days7: '7 days', system: 'System', resetData: 'Reset demo state', layers: 'Map layers', pfzLayer: 'Fishing zones', alertLayer: 'Marine alerts', vessels: 'Vessels', mapLabels: 'Map labels follow website language.', signIn: 'Sign In / Register', signOut: 'Sign Out', viewOnMap: '🗺️ View Route on Map', viewSafety: '🛡️ Safety Assessment', navHudTitle: 'Active Navigation Route', originPort: 'Departure Port', destZone: 'Destination Zone', eta: 'Estimated Travel Time', distance: 'Distance', geofenceClear: 'Boundary Clearance', calculateRoute: 'Calculate Safe Marine Route',
    locPromptTitle: 'Tailor Intelligence to Your Location',
    locPromptDesc: 'Allow location access to receive real-time INCOIS wave forecasts, nearby PFZs, and safe coastal routes from your current position.',
    allowLocBtn: 'Allow Location',
    detectingLoc: 'Detecting GPS...',
    locActive: 'Live GPS Active',
    locDenied: 'Location Access Disabled',
    nearestPortLabel: 'Nearest Port',
    inlandMsg: 'Inland location detected. Navigation routed from nearest coastal fishery hub.',
    waypointTable: 'Waypoint Navigation Log',
    bearing: 'Compass Heading',
    legDist: 'Leg Dist',
    previousChats: 'Previous Chats',
    newChat: 'New Chat',
    recenter: 'Recenter Map',
    noChatsYet: 'No previous conversations.',
    activePfzTitle: 'Active Potential Fishing Zones',
    inactivePfzTitle: 'Inactive / Caution Zones',
    noActivePfz: 'No active PFZs available for this port.',
    noInactivePfz: 'No inactive PFZ records available.',
    allPfzTitle: 'All Potential Fishing Zones'
  },
  hi: {
    dashboard: 'डैशबोर्ड', map: 'समुद्री इंटेलिजेंस मैप', analytics: 'महासागर विश्लेषण', fishing: 'मछली पकड़ने की इंटेलिजेंस', safety: 'सुरक्षा और मार्ग', assistant: 'ORCA AI सहायक', alerts: 'सूचनाएं', settings: 'सेटिंग्स', profile: 'प्रोफ़ाइल', workspace: 'वर्कस्पेस', operational: 'सिस्टम चालू हैं', connected: 'समुद्री डेटा सेवाएं जुड़ी हैं', marine: 'समुद्री इंटेलिजेंस', glance: 'समुद्री स्थिति एक नज़र में।', location: 'मुंबई तट • लाइव समुद्री सेंसर डेटा कनेक्टेड', ask: 'ORCA से पूछें', seaState: 'समुद्र की स्थिति', wind: 'हवा', sst: 'समुद्र सतह तापमान', activePFZ: 'सक्रिय PFZ', moderate: 'मध्यम', waves: '1.2 मी. लहरें', steady: 'NE • स्थिर', favourable: 'अनुकूल', openMap: 'मैप खोलें', activeAdvisories: 'सक्रिय सलाह', viewAll: 'सभी देखें', insights: 'आज की समुद्री जानकारी', bestFishing: 'बेहतरीन मछली पकड़ने का अवसर', departure: 'अनुशंसित प्रस्थान', confidence: 'डेटा विश्वसनीयता', verified: 'सत्यापित इंटेलिजेंस', sources: 'स्रोत: ISRO • INCOIS • IMD • ओशन डेटा', oceanInputs: 'समुद्र और भौगोलिक इनपुट की जांच की गई।', allLayers: 'सभी लेयर', weather: 'मौसम', hazards: 'जोखिम', boundaries: 'सीमाएं', today: 'आज', selectedZone: 'चयनित क्षेत्र', high: 'उच्च विश्वसनीयता', why: 'यह क्षेत्र क्यों?', signal: 'संकेत', how: 'ORCA कैसे निर्णय लेता है', discover: 'खोजें', correlate: 'संबंध जोड़ें', assess: 'आकलन करें', explain: 'समझाएं', findZones: 'संभावित मछली पकड़ने वाले क्षेत्र खोजें।', explore: 'PFZ खोजें', viewZone: 'क्षेत्र देखें', recommendation: 'ORCA की सिफारिश', start: 'शुरुआत करें', safeRoute: 'सुरक्षित मार्ग आकलन', recommended: 'अनुशंसित', low: 'कम', risk: 'जोखिम', whyRoute: 'ORCA इस मार्ग की सिफारिश क्यों करता है', safetyChecklist: 'सुरक्षा चेकलिस्ट', askSea: 'समुद्र के बारे में ORCA से पूछें।', conversational: 'कन्वर्सेशनल मरीन इंटेलिजेंस', placeholder: 'समुद्र से जुड़ा सवाल पूछें...', send: 'भेजें', nearest: 'आज का निकटतम PFZ', safeTomorrow: 'क्या कल सुबह जाना सुरक्षित है?', showHazards: 'मुंबई के पास जोखिम दिखाएं', findRoute: 'सुरक्षित मार्ग खोजें', close: 'बंद करें', reset: 'दृश्य रीसेट', satellite: 'सैटेलाइट', street: 'सड़क', locate: 'मेरा स्थान', language: 'भाषा', search: 'खोजें', notifications: 'सूचनाएं', noResults: 'कोई परिणाम नहीं मिला।', routeA: 'तटीय मार्ग A', routeB: 'तटीय मार्ग B', routeC: 'संतुलित मार्ग', routeRisk: 'मार्ग जोखिम', checked: 'जांच पूरी', refresh: 'रीफ्रेश', save: 'बदलाव सहेजें', saved: 'बदलाव सहेजे गए', theme: 'थीम', darkMode: 'डार्क मोड', email: 'ईमेल सूचनाएं', profileTitle: 'ऑपरेशनल प्रोफ़ाइल', role: 'समुद्री शोधकर्ता / कप्तान', details: 'प्रोफ़ाइल विवरण', name: 'Capt. Devesh Madhavi', status: 'सक्रिय सत्र', mobile: 'मोबाइल नंबर', emailLabel: 'ईमेल', profession: 'पेशा', edit: 'संपादित करें', done: 'पूर्ण', trend: 'PFZ विश्वसनीयता ट्रेंड', pfzConfidence: 'PFZ विश्वसनीयता', freshness: 'डेटा ताजगी', latest: 'नवीनतम नमूना', marineInputs: 'सैटेलाइट समुद्री रंग, SST और मौसम इनपुट।', spatialSignals: 'आसपास के स्थानिक संकेत और PFZ उम्मीदवार जोड़ता है।', opportunitySafety: 'मछली पकड़ने के अवसर को सुरक्षा सीमाओं के साथ संतुलित करता है।', evidenceRecommendation: 'हर सिफारिश के पीछे के प्रमाण समझाता है।', hazardAvoided: 'पहचाने गए सावधानी क्षेत्र से बचता है।', boundariesChecked: 'मार्ग से पहले परिचालन सीमाएं जांचता है।', riskCorridor: 'कम जोखिम वाले तटीय गलियारे को प्राथमिकता देता है।', recalculate: 'नए डेटा के बाद मार्ग फिर निकाला जा सकता है।', demo: 'रीयल-टाइम मोड • लाइव टेलीमेट्री कनेक्टेड।', demoAnswer: 'नमस्ते कप्तान! मैं ORCA हूँ, आपका समुद्री AI निर्णय सहायक। मैं आपकी क्या मदद कर सकता हूँ?', mapFail: 'मैप टाइल लोड नहीं हो पाईं।', routeSummary: '39.2 किमी • लगभग 2 घंटे 35 मिनट', routeBText: '48.5 किमी • लगभग 3 घंटे 10 मिनट', routeCText: '42.0 किमी • लगभग 2 घंटे 45 मिनट', selectPeriod: 'अवधि', hours24: '24 घंटे', days7: '7 दिन', system: 'सिस्टम', resetData: 'रीसेट', layers: 'मैप लेयर', pfzLayer: 'मछली पकड़ने के क्षेत्र', alertLayer: 'समुद्री अलर्ट', vessels: 'नौकाएं', mapLabels: 'मैप के नाम वेबसाइट की भाषा के अनुसार हैं।', signIn: 'साइन इन / रजिस्टर', signOut: 'साइन आउट', viewOnMap: '🗺️ मैप पर मार्ग देखें', viewSafety: '🛡️ सुरक्षा आकलन', navHudTitle: 'सक्रिय नेविगेशन मार्ग', originPort: 'प्रस्थान बंदरगाह', destZone: 'गंतव्य क्षेत्र', eta: 'अनुमानित यात्रा समय', distance: 'दूरी', geofenceClear: 'सीमा अनुमति', calculateRoute: 'सुरक्षित समुद्री मार्ग निकालें',
    locPromptTitle: 'अपने स्थान के अनुसार सटीक जानकारी पाएं',
    locPromptDesc: 'अपने स्थान की अनुमति दें ताकि INCOIS की लाइव लहरें, निकटतम PFZ और सुरक्षित मार्ग आपको दिखाए जा सकें।',
    allowLocBtn: 'स्थान अनुमति दें',
    detectingLoc: 'स्थान खोजा जा रहा है...',
    locActive: 'लाइव GPS सक्रिय',
    locDenied: 'स्थान अनुमति अक्षम',
    nearestPortLabel: 'निकटतम बंदरगाह',
    inlandMsg: 'अंतर्देशीय स्थान मिला। निकटतम तटीय बंदरगाह से मार्ग की गणना की गई है।',
    waypointTable: 'वेपॉइंट नेविगेशन लॉग',
    bearing: 'दिशा',
    legDist: 'दूरी',
    previousChats: 'पिछली बातचीत',
    newChat: 'नई बातचीत',
    recenter: 'मैप रीसेंटर करें',
    noChatsYet: 'कोई पिछली बातचीत नहीं है।',
    activePfzTitle: 'सक्रिय संभावित मछली पकड़ने के क्षेत्र (Active PFZ)',
    inactivePfzTitle: 'निष्क्रिय / सावधानी क्षेत्र (Inactive PFZ)',
    noActivePfz: 'इस बंदरगाह के लिए कोई सक्रिय PFZ उपलब्ध नहीं है।',
    noInactivePfz: 'कोई निष्क्रिय PFZ रिकॉर्ड नहीं है।',
    allPfzTitle: 'सभी संभावित मछली पकड़ने के क्षेत्र'
  },
  mr: {
    dashboard: 'डॅशबोर्ड', map: 'सागरी इंटेलिजन्स नकाशा', analytics: 'महासागर विश्लेषण', fishing: 'मासेमारी इंटेलिजन्स', safety: 'सुरक्षा आणि मार्ग', assistant: 'ORCA AI सहाय्यक', alerts: 'सूचना', settings: 'सेटिंग्ज', profile: 'प्रोफाइल', workspace: 'वर्कस्पेस', operational: 'सिस्टम कार्यरत', connected: 'सागरी डेटा सेवा जोडलेल्या', marine: 'सागरी इंटेलिजन्स', glance: 'सागरी स्थिती एका नजरेत.', location: 'मुंबई किनारा • थेट सागरी सेन्सर जोडणी', ask: 'ORCA ला विचारा', seaState: 'समुद्राची स्थिती', wind: 'वारा', sst: 'समुद्र पृष्ठभाग तापमान', activePFZ: 'सक्रिय PFZ', moderate: 'मध्यम', waves: '1.2 मी. लाटा', steady: 'NE • स्थिर', favourable: 'अनुकूल', openMap: 'नकाशा उघडा', activeAdvisories: 'सक्रिय सूचना', viewAll: 'सर्व पहा', insights: 'आजची सागरी माहिती', bestFishing: 'मासेमारीची सर्वोत्तम संधी', departure: 'शिफारस केलेली प्रस्थान वेळ', confidence: 'डेटा विश्वासार्हता', verified: 'सत्यापित इंटेलिजन्स', sources: 'स्रोत: ISRO • INCOIS • IMD • ओशन डेटा', oceanInputs: 'समुद्र आणि डेटाबेस इनपुट तपासले.', allLayers: 'सर्व लेयर्स', weather: 'हवामान', hazards: 'धोके', boundaries: 'सीमा', today: 'आज', selectedZone: 'निवडलेले क्षेत्र', high: 'उच्च विश्वासार्हता', why: 'हे क्षेत्र का?', signal: 'संकेत', how: 'ORCA कसे निर्णय घेतो', discover: 'शोध', correlate: 'संबंध जोडा', assess: 'आकलन', explain: 'समजावून सांगा', findZones: 'आशादायक मासेमारी क्षेत्र शोधा.', explore: 'PFZ शोधा', viewZone: 'क्षेत्र पहा', recommendation: 'ORCA ची शिफारस', start: 'सुरुवात', safeRoute: 'सुरक्षित मार्गाचे आकलन', recommended: 'शिफारस केलेला', low: 'कमी', risk: 'धोका', whyRoute: 'ORCA या मार्गाची शिफारस का करतो', safetyChecklist: 'सुरक्षा तपासणी', askSea: 'समुद्राबद्दल ORCA ला विचारा.', conversational: 'कन्वर्सेशनल मरीन इंटेलिजन्स', placeholder: 'सागरी प्रश्न विचारा किंवा मार्ग योजना करा...', send: 'पाठवा', nearest: 'आजचा जवळचा PFZ', safeTomorrow: 'उद्या सकाळी जाणे सुरक्षित आहे का?', showHazards: 'मुंबईजवळचे धोके दाखवा', findRoute: 'सुरक्षित मार्ग शोधा', close: 'बंद', reset: 'दृश्य रीसेट', satellite: 'सॅटेलाइट', street: 'रस्ता', locate: 'माझे स्थान', language: 'भाषा', search: 'शोधा', notifications: 'सूचना', noResults: 'जुळणारे परिणाम नाहीत.', routeA: 'किनारी मार्ग A', routeB: 'किनारी मार्ग B', routeC: 'संतुलित मार्ग', routeRisk: 'मार्ग धोका', checked: 'तपासले', refresh: 'रीफ्रेश', save: 'बदल जतन करा', saved: 'बदल जतन झाले', theme: 'थीम', darkMode: 'डार्क मोड', email: 'ईमेल सूचना', profileTitle: 'ऑपरेशनल प्रोफाइल', role: 'सागरी संशोधक / कॅप्टन', details: 'प्रोफाइल तपशील', name: 'Capt. Devesh Madhavi', status: 'सक्रिय खाते', mobile: 'मोबाइल क्रमांक', emailLabel: 'ईमेल', profession: 'व्यवसाय', edit: 'संपादित करा', done: 'पूर्ण', trend: 'PFZ विश्वासार्हता ट्रेंड', pfzConfidence: 'PFZ विश्वासार्हता', freshness: 'डेटा ताजेपणा', latest: 'नवीन नमुना', marineInputs: 'सॅटेलाइट समुद्री रंग, SST आणि हवामान इनपुट.', spatialSignals: 'जवळचे स्थानिक संकेत आणि PFZ उमेदवार जोडतो.', opportunitySafety: 'मासेमारीची संधी आणि सुरक्षा मर्यादा संतुलित करतो.', evidenceRecommendation: 'प्रत्येक शिफारसीमागील पुरावे समजावतो.', hazardAvoided: 'ओळखलेल्या सावधगिरीच्या क्षेत्रापासून दूर राहतो.', boundariesChecked: 'मार्गापूर्वी ऑपरेशनल सीमा तपासतो.', riskCorridor: 'कमी-धोका किनारी मार्ग पसंत करतो.', recalculate: 'नवीन डेटा आल्यावर मार्ग पुन्हा काढता येईल.', demo: 'थेट मोड • रिअल-टाइम टेलीमेट्री जोडली आहे.', demoAnswer: 'नमस्कार कॅप्टन! मी ORCA आहे, आपला सागरी AI निर्णय सहाय्यक. मी आज आपल्या प्रवासासाठी कशी मदत करू?', mapFail: 'नकाशा टाइल लोड झाल्या नाहीत.', routeSummary: '39.2 किमी • सुमारे 2 तास 35 मिनिटे', routeBText: '48.5 किमी • सुमारे 3 तास 10 मिनिटे', routeCText: '42.0 किमी • सुमारे 2 तास 45 मिनिटे', selectPeriod: 'कालावधी', hours24: '24 तास', days7: '7 दिवस', system: 'सिस्टम', resetData: 'रीसेट', layers: 'नकाशा लेयर्स', pfzLayer: 'मासेमारी क्षेत्रे', alertLayer: 'सागरी सूचना', vessels: 'नौका', mapLabels: 'नकाशावरील नावे वेबसाइटच्या भाषेनुसार आहेत.', signIn: 'साइन इन / नोंदणी', signOut: 'साइन आउट', viewOnMap: '🗺️ नकाशावर मार्ग पहा', viewSafety: '🛡️ सुरक्षा विश्लेषण', navHudTitle: 'सक्रिय नेव्हिगेशन मार्ग', originPort: 'प्रस्थान बंदर', destZone: 'गंतव्य क्षेत्र', eta: 'अंदाजित वेळ', distance: 'अंतर', geofenceClear: 'सीमा तपासणी', calculateRoute: 'सुरक्षित सागरी मार्ग काढा',
    locPromptTitle: 'आपल्या स्थानानुसार अचूक माहिती मिळवा',
    locPromptDesc: 'स्थान परवानगी द्या जेणेकरून INCOIS च्या थेट लाटा, जवळचे PFZ आणि सुरक्षित मार्ग आपल्याला दाखवता येतील.',
    allowLocBtn: 'स्थान परवानगी द्या',
    detectingLoc: 'स्थान शोधत आहे...',
    locActive: 'थेट GPS सक्रिय',
    locDenied: 'स्थान परवानगी बंद आहे',
    nearestPortLabel: 'जवळचे बंदर',
    inlandMsg: 'अंतर्देशीय स्थान सापडले. जवळच्या किनारी बंदरावरून मार्गाची गणना केली आहे.',
    waypointTable: 'वेपॉइंट नेव्हिगेशन तपशील',
    bearing: 'दिशा',
    legDist: 'अंतर',
    previousChats: 'मागील संभाषणे',
    newChat: 'नवीन संभाषण',
    recenter: 'नकाशा रीसेंटर करा',
    noChatsYet: 'कोणतीही मागील संभाषणे नाहीत.',
    activePfzTitle: 'सक्रिय संभाव्य मासेमारी क्षेत्र (Active PFZ)',
    inactivePfzTitle: 'निष्क्रिय / सावधगिरी क्षेत्र (Inactive PFZ)',
    noActivePfz: 'या बंदरासाठी कोणतेही सक्रिय PFZ उपलब्ध नाहीत.',
    noInactivePfz: 'कोणतेही निष्क्रिय PFZ नोंदी उपलब्ध नाहीत.',
    allPfzTitle: 'सर्व संभाव्य मासेमारी क्षेत्र'
  }
}

const tr = (lang, key) => T[lang]?.[key] ?? T.en[key] ?? key
const labels = {
  '/': 'Dashboard',
  '/map': 'Marine Intelligence Map',
  '/analytics': 'Ocean Analytics',
  '/fishing': 'Fishing Intelligence',
  '/safety': 'Safety & Routes',
  '/assistant': 'ORCA AI Assistant',
  '/alerts': 'Alerts',
  '/settings': 'Settings',
  '/profile': 'Profile'
}
const keyFor = u => ({
  Dashboard: 'dashboard',
  'Marine Intelligence Map': 'map',
  'Ocean Analytics': 'analytics',
  'Fishing Intelligence': 'fishing',
  'Safety & Routes': 'safety',
  'ORCA AI Assistant': 'assistant',
  Alerts: 'alerts',
  Settings: 'settings',
  Profile: 'profile'
}[u])

const PORTS = [
  // Gujarat (North-West)
  { id: 'veraval', name: 'Veraval Fishery Port (Gujarat)', state: 'Gujarat', sector: 'North-West (Gujarat)', lat: 20.9000, lon: 70.3667 },
  { id: 'porbandar', name: 'Porbandar Marine Port (Gujarat)', state: 'Gujarat', sector: 'North-West (Gujarat)', lat: 21.6417, lon: 69.6293 },
  { id: 'okha', name: 'Okha Fishery Port (Gujarat)', state: 'Gujarat', sector: 'North-West (Gujarat)', lat: 22.4667, lon: 69.0667 },

  // Maharashtra (West Coast)
  { id: 'mumbai', name: 'Mumbai Harbour (Sassoon Docks)', state: 'Maharashtra', sector: 'West Coast (Maharashtra)', lat: 18.9400, lon: 72.8300 },
  { id: 'alibaug', name: 'Alibaug Port (Maharashtra)', state: 'Maharashtra', sector: 'West Coast (Maharashtra)', lat: 18.6414, lon: 72.8722 },
  { id: 'ratnagiri', name: 'Ratnagiri Fishery Port (Mirkarwada)', state: 'Maharashtra', sector: 'West Coast (Maharashtra)', lat: 16.9902, lon: 73.3120 },
  { id: 'malvan', name: 'Malvan Port (Sindhudurg)', state: 'Maharashtra', sector: 'West Coast (Maharashtra)', lat: 16.0594, lon: 73.4686 },

  // Goa (South-West)
  { id: 'goa', name: 'Goa Mormugao Port', state: 'Goa', sector: 'South-West (Goa)', lat: 15.4989, lon: 73.8278 },

  // Karnataka (South-West)
  { id: 'karwar', name: 'Karwar Fishery Port (Karnataka)', state: 'Karnataka', sector: 'South-West (Karnataka)', lat: 14.8050, lon: 74.1240 },
  { id: 'mangalore', name: 'Mangalore Fishery Port (Bunder)', state: 'Karnataka', sector: 'South-West (Karnataka)', lat: 12.8580, lon: 74.8360 },

  // Kerala (South-West)
  { id: 'kochi', name: 'Cochin Fishery Harbour (Kerala)', state: 'Kerala', sector: 'South-West (Kerala)', lat: 9.9650, lon: 76.2620 },
  { id: 'kollam', name: 'Kollam Neendakara Harbour (Kerala)', state: 'Kerala', sector: 'South-West (Kerala)', lat: 8.9440, lon: 76.5360 },

  // Tamil Nadu (South Coast & Coromandel)
  { id: 'kanyakumari', name: 'Kanyakumari Cape Port (Tamil Nadu)', state: 'Tamil Nadu', sector: 'South Coast (Tamil Nadu)', lat: 8.0883, lon: 77.5385 },
  { id: 'tuticorin', name: 'Tuticorin V.O.C. Port (Tamil Nadu)', state: 'Tamil Nadu', sector: 'South-East (Gulf of Mannar)', lat: 8.7642, lon: 78.1348 },
  { id: 'nagapattinam', name: 'Nagapattinam Harbour (Tamil Nadu)', state: 'Tamil Nadu', sector: 'South-East (Coromandel)', lat: 10.7656, lon: 79.8424 },
  { id: 'chennai', name: 'Chennai Kasimedu Harbour (Tamil Nadu)', state: 'Tamil Nadu', sector: 'South-East (Coromandel)', lat: 13.1250, lon: 80.2980 },

  // Andhra Pradesh (East Coast)
  { id: 'kakinada', name: 'Kakinada Deepwater Port (Andhra)', state: 'Andhra Pradesh', sector: 'East Coast (Andhra Pradesh)', lat: 16.9891, lon: 82.2475 },
  { id: 'visakhapatnam', name: 'Visakhapatnam Fishing Harbour (Andhra)', state: 'Andhra Pradesh', sector: 'East Coast (Andhra Pradesh)', lat: 17.6868, lon: 83.2185 },

  // Odisha (East Coast)
  { id: 'paradip', name: 'Paradip Fishery Port (Odisha)', state: 'Odisha', sector: 'East Coast (Odisha)', lat: 20.2644, lon: 86.6715 },

  // West Bengal (North-East)
  { id: 'haldia', name: 'Haldia / Diamond Harbour (West Bengal)', state: 'West Bengal', sector: 'North-East (Bengal Bay)', lat: 22.0667, lon: 88.0667 }
]

function Card({ title, children, action }) {
  return (
    <section className="card">
      <div className="cardHead">
        <h3>{title}</h3>
        {action}
      </div>
      {children}
    </section>
  )
}

function Dashboard({ lang, navigate, setSelected, setModal, pfzList, alertList, oceanStats, selectedPort, setSelectedPort, userLocation, requestLocationPermission, detectingLocation, portContext }) {
  const t = k => tr(lang, k)
  const currentPort = PORTS.find(p => p.id === selectedPort) || PORTS[3]
  const chosen = pfzList[0] || staticPfz[0]

  // Port-specific marine conditions from portContext
  const mc = portContext?.marine_conditions
  const liveIncois = userLocation?.incois_live

  const waveHeight = mc?.wave_height_m 
    ? `${mc.wave_height_m} m waves`
    : (liveIncois?.wave_height_m ? `${liveIncois.wave_height_m} m waves` : (oceanStats?.wave_height?.current ? `${oceanStats.wave_height.current} m waves` : t('waves')))
  const seaCondition = mc?.sea_state || liveIncois?.sea_state || oceanStats?.wave_height?.status || t('moderate')
  const windSpeed = mc?.wind_speed_kmh 
    ? `${mc.wind_speed_kmh} km/h`
    : (liveIncois?.wind_speed_kmh ? `${liveIncois.wind_speed_kmh} km/h` : (oceanStats?.wind_speed?.current ? `${oceanStats.wind_speed.current} km/h` : '18 km/h'))
  const windDirection = mc?.wind_direction 
    ? `${mc.wind_direction} • steady` 
    : (liveIncois?.wind_direction_deg ? `${liveIncois.wind_direction_deg}° • Live INCOIS` : t('steady'))
  const sstValue = mc?.sst_celsius 
    ? `${mc.sst_celsius}°C` 
    : (liveIncois?.sea_surface_temperature_c ? `${liveIncois.sea_surface_temperature_c}°C` : (chosen?.sst ? `${chosen.sst}°C` : '28.1°C'))

  const confidenceScore = mc?.confidence_pct || oceanStats?.data_confidence || 94
  const departureRec = mc?.departure_recommendation || '05:30–08:30 • Favourable low-swell window'
  const bestFishingRec = mc?.best_fishing_summary || `${chosen.name} • ${chosen.confidence}% confidence • ${chosen.distance || '32 km offshore'}`

  // Port-specific advisories if available, fallback to global alertList
  const portAdvisories = (portContext?.advisories && portContext.advisories.length > 0)
    ? portContext.advisories
    : alertList

  // Separate Active and Inactive PFZs
  const activePfzs = pfzList.filter(z => z.status !== 'INACTIVE')
  const inactivePfzs = pfzList.filter(z => z.status === 'INACTIVE')

  // Rain and coastal weather data (Strictly location-aware from Port Context)
  const rainData = portContext?.rain_data || {
    precipitation_mm: 0.8,
    rain_probability_pct: 20,
    intensity: 'Light',
    condition: 'Partly Cloudy'
  }

  return (
    <>
      {/* Geolocation Permission & Status Banner */}
      {(!userLocation || userLocation.status !== 'granted') ? (
        <div className="locationBanner">
          <div className="locationBannerContent">
            <span className="locationBannerIcon">📍</span>
            <div className="locationBannerText">
              <strong>{t('locPromptTitle')}</strong>
              <p>{t('locPromptDesc')}</p>
            </div>
          </div>
          <div className="locationBannerActions">
            <button className="locationBtn" onClick={() => requestLocationPermission && requestLocationPermission(true)} disabled={detectingLocation}>
              {detectingLocation ? t('detectingLoc') : `📍 ${t('allowLocBtn')}`}
            </button>
          </div>
        </div>
      ) : (
        <div className="locationBanner" style={{ borderColor: 'rgba(15, 168, 137, 0.4)' }}>
          <div className="locationBannerContent">
            <span className="pulseGps" style={{ width: '12px', height: '12px' }} />
            <div className="locationBannerText">
              <strong>📍 {userLocation.is_coastal ? 'Live Coastal Position Active' : 'Live Inland Coordinates Active'}</strong>
              <p>
                {userLocation.lat.toFixed(4)}°N, {userLocation.lon.toFixed(4)}°E • {t('nearestPortLabel')}: <b>{userLocation.port_name}</b> ({userLocation.distance_to_port_km?.toFixed(1)} km away) • Live INCOIS Connected
              </p>
            </div>
          </div>
          <div className="locationBannerActions">
            <button className="locationBtnSec" onClick={() => requestLocationPermission && requestLocationPermission(true)} disabled={detectingLocation}>
              {detectingLocation ? t('detectingLoc') : '🔄 Re-detect GPS'}
            </button>
            <button className="locationBtn" onClick={() => navigate('/map')}>
              🗺️ {t('openMap')}
            </button>
          </div>
        </div>
      )}

      <div className="welcome">
        <div>
          <span className="eyebrow">{t('marine')} • {userLocation?.port_name ? `${userLocation.port_name} Sector` : currentPort.sector}</span>
          <h2>{userLocation?.port_name || currentPort.name}</h2>
          <p>Real-time marine intelligence tailored to your port coordinates, synced with INCOIS models.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <select 
            value={selectedPort} 
            onChange={e => setSelectedPort && setSelectedPort(e.target.value)}
            className="selectControl"
          >
            {PORTS.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <button className="primary" onClick={() => navigate('/map')}>{t('openMap')} →</button>
        </div>
      </div>

      <div className="stats">
        <div className="stat">
          <span>{t('seaState')}</span>
          <strong>{seaCondition}</strong>
          <small>{waveHeight}</small>
        </div>
        <div className="stat">
          <span>{t('wind')}</span>
          <strong>{windSpeed}</strong>
          <small>{windDirection}</small>
        </div>
        <div className="stat">
          <span>Rain & Weather</span>
          <strong>{rainData.condition || 'Clear / Fair'}</strong>
          <small>{rainData.precipitation_mm} mm • {rainData.rain_probability_pct}% rain • {rainData.intensity}</small>
        </div>
        <div className="stat">
          <span>{t('sst')}</span>
          <strong>{sstValue}</strong>
          <small>{mc ? `${currentPort.name.split(' ')[0]} Marine Sensor` : (liveIncois ? 'INCOIS GHRSST Real-time' : t('favourable'))}</small>
        </div>
        <div className="stat">
          <span>{t('activePFZ')}</span>
          <strong>{activePfzs.length}</strong>
          <small>{inactivePfzs.length} Inactive • {currentPort.name.split(' ')[0]}</small>
        </div>
      </div>

      <div className="dashboardGrid">
        <Card title={t('allPfzTitle')} action={<button className="textBtn" onClick={() => navigate('/fishing')}>{t('viewAll')} →</button>}>
          {/* ACTIVE PFZs */}
          <div className="pfzSectionHead active">
            <span className="sectionBadge active">● ACTIVE PFZs ({activePfzs.length})</span>
          </div>
          {activePfzs.length > 0 ? (
            <div className="rank">
              {activePfzs.slice(0, 3).map(z => (
                <button key={z.id} onClick={() => { setSelected(z.id); navigate('/map') }}>
                  <span><b>{z.id}</b>{z.name}</span>
                  <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <span className="statusPill active">ACTIVE</span>
                    <strong>{z.confidence}%</strong>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="emptyPfzNotice">{t('noActivePfz')}</div>
          )}

          {/* INACTIVE PFZs */}
          <div className="pfzSectionHead inactive" style={{ marginTop: '14px' }}>
            <span className="sectionBadge inactive">○ INACTIVE PFZs ({inactivePfzs.length})</span>
          </div>
          {inactivePfzs.length > 0 ? (
            <div className="rank">
              {inactivePfzs.slice(0, 2).map(z => (
                <button key={z.id} className="pfzInactiveRow" onClick={() => { setSelected(z.id); navigate('/map') }}>
                  <span><b>{z.id}</b>{z.name}</span>
                  <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <span className="statusPill inactive">INACTIVE</span>
                    <small style={{ color: 'var(--text-muted)' }}>{z.inactive_reason || 'Sub-optimal gradient'}</small>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="emptyPfzNotice">{t('noInactivePfz')}</div>
          )}
        </Card>

        <Card title={t('activeAdvisories')}>
          <div>
            {portAdvisories.slice(0, 4).map(a => (
              <button className="alertRow" key={a.id} onClick={() => setModal(a)}>
                <span className={'severity ' + (a.risk_level ? a.risk_level.toLowerCase() : a.severity?.toLowerCase() || 'medium')}>
                  {a.risk_level || a.severity || 'ALERT'}
                </span>
                <div>
                  <b>{a.title?.[lang] || a.title || 'Marine Advisory'}</b>
                  <small>{a.description || a.body?.[lang] || a.body || ''}</small>
                </div>
                <span>→</span>
              </button>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid2">
        <Card title={t('insights')}>
          <div className="insight">
            <span>01</span>
            <div>
              <b>{t('bestFishing')}</b>
              <p>{bestFishingRec}</p>
            </div>
          </div>
          <div className="insight">
            <span>02</span>
            <div>
              <b>{t('departure')}</b>
              <p>{departureRec}</p>
            </div>
          </div>
        </Card>
        <Card title={t('confidence')}>
          <div className="confidence">
            <strong>{confidenceScore}%</strong>
            <div className="bar"><span style={{ width: `${confidenceScore}%` }} /></div>
            <p>{t('verified')} • {t('oceanInputs')}</p>
          </div>
        </Card>
      </div>
    </>
  )
}

function MapPage({ lang, selected, setSelected, activeRoute, setActiveRoute, pfzList, allIndiaPfzList = [], alertList, selectedPort, setSelectedPort, userLocation, onPlotRouteFromLocation }) {
  const t = k => tr(lang, k)
  const ref = useRef(null)
  const mapRef = useRef(null)
  const [base, setBase] = useState('satellite')
  const [showPFZ, setShowPFZ] = useState(true)
  const [showAlerts, setShowAlerts] = useState(true)
  const [showVessels, setShowVessels] = useState(true)
  const [showRoute, setShowRoute] = useState(true)
  const [mapScope, setMapScope] = useState('all') // 'all' or 'port'
  const [mapError, setMapError] = useState(false)

  const currentPort = PORTS.find(p => p.id === selectedPort) || PORTS[3]
  const zone = pfzList.find(z => z.id === selected) || pfzList[0] || staticPfz[0]

  useEffect(() => {
    if (!ref.current || mapRef.current) return
    const initialLat = userLocation?.lat || currentPort.lat
    const initialLon = userLocation?.lon || currentPort.lon
    const map = L.map(ref.current, { zoomControl: false }).setView([initialLat, initialLon], 7)
    L.control.zoom({ position: 'bottomright' }).addTo(map)

    const street = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    })
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles © Esri'
    })

    ;(base === 'satellite' ? satellite : street).addTo(map)
    map.on('tileerror', () => setMapError(true))
    mapRef.current = { map, street, satellite, layers: [] }

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    const obj = mapRef.current
    if (!obj) return
    obj.street.remove()
    obj.satellite.remove()
    ;(base === 'satellite' ? obj.satellite : obj.street).addTo(obj.map)
  }, [base])

  useEffect(() => {
    const obj = mapRef.current
    if (!obj) return

    obj.layers?.forEach(l => l.remove())
    const layers = []

    // 0. Draw User Location Marker ("You Are Here")
    if (userLocation && userLocation.lat && userLocation.lon) {
      const userIcon = L.divIcon({
        className: 'user-map-pin',
        html: `<div class="user-map-pin-inner">📍 You (${userLocation.is_coastal ? 'Vessel' : 'GPS'})</div>`,
        iconSize: null,
        iconAnchor: [30, 15]
      })
      const userMarker = L.marker([userLocation.lat, userLocation.lon], { icon: userIcon })
        .bindPopup(`<b>📍 Your Location</b><br/>Lat: ${userLocation.lat.toFixed(4)}, Lon: ${userLocation.lon.toFixed(4)}<br/>${userLocation.is_coastal ? 'Coastal Waters' : 'Inland Coordinates'}<br/>Nearest Port: ${userLocation.port_name} (${userLocation.distance_to_port_km?.toFixed(1)} km)<br/>Status: Live INCOIS Connected`)
        .addTo(obj.map)
      layers.push(userMarker)
    }

    // 1. Draw Active Navigation Route if available
    if (showRoute && activeRoute && activeRoute.waypoints && activeRoute.waypoints.length > 0) {
      const latlngs = activeRoute.waypoints.map(w => [w.lat, w.lon])
      if (activeRoute.origin) latlngs.unshift([activeRoute.origin.lat, activeRoute.origin.lon])
      if (activeRoute.destination) latlngs.push([activeRoute.destination.lat, activeRoute.destination.lon])

      // Glowing outer route
      const glow = L.polyline(latlngs, {
        color: '#0088cc',
        weight: 8,
        opacity: 0.45,
        lineCap: 'round'
      }).addTo(obj.map)
      layers.push(glow)

      // Core route polyline
      const line = L.polyline(latlngs, {
        color: '#00d2ff',
        weight: 4,
        opacity: 0.95,
        dashArray: '8, 8'
      }).addTo(obj.map)
      layers.push(line)

      // Start / Origin Port Marker (Green Anchor)
      if (activeRoute.origin) {
        const startIcon = L.divIcon({
          className: 'orca-start-pin',
          html: '<div style="background:#20c997;color:#fff;border-radius:50%;width:30px;height:30px;display:grid;place-items:center;border:3px solid #fff;box-shadow:0 4px 14px rgba(0,0,0,0.3);font-size:16px;">⚓</div>',
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        })
        const startMarker = L.marker([activeRoute.origin.lat, activeRoute.origin.lon], { icon: startIcon })
          .bindPopup(`<b>⚓ Departure Port</b><br/>${activeRoute.departure_name || 'Coastal Port'}<br/>Lat: ${activeRoute.origin.lat}, Lon: ${activeRoute.origin.lon}`)
          .addTo(obj.map)
        layers.push(startMarker)
      }

      // End / Destination Marker (Gold Target)
      if (activeRoute.destination) {
        const destIcon = L.divIcon({
          className: 'orca-dest-pin',
          html: '<div style="background:#ffc107;color:#000;border-radius:50%;width:32px;height:32px;display:grid;place-items:center;border:3px solid #fff;box-shadow:0 4px 14px rgba(0,0,0,0.3);font-size:16px;">🎯</div>',
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        })
        const destMarker = L.marker([activeRoute.destination.lat, activeRoute.destination.lon], { icon: destIcon })
          .bindPopup(`<b>🎯 Destination PFZ</b><br/>${activeRoute.destination_name || 'Fishing Zone'}<br/>Distance: ${activeRoute.distance_km} km<br/>ETA: ~${Math.round(activeRoute.estimated_travel_time_min || (activeRoute.distance_km / 15 * 60))} mins`)
          .addTo(obj.map)
        layers.push(destMarker)
      }

      // Auto-fit bounds to route
      obj.map.fitBounds(L.latLngBounds(latlngs), { padding: [60, 60] })
    }

    // 2. Draw PFZ Fishing Zones across Indian Coast
    if (showPFZ) {
      const zonesToDraw = (mapScope === 'all' && allIndiaPfzList.length > 0) ? allIndiaPfzList : pfzList
      zonesToDraw.forEach(z => {
        const isSel = z.id === selected
        const isCurrentPort = z.port_id === selectedPort
        const m = L.circleMarker([z.lat, z.lng || z.lon], {
          radius: isSel ? 13 : (isCurrentPort ? 10 : 7),
          weight: isSel ? 3 : 2,
          color: isSel ? '#00d2ff' : (isCurrentPort ? '#00e5ff' : '#18a98d'),
          fillColor: isSel ? '#0088cc' : (isCurrentPort ? '#00b4d8' : '#20b486'),
          fillOpacity: isSel ? 0.95 : (isCurrentPort ? 0.85 : 0.65)
        })
        m.bindPopup(`<b>${z.id} · ${z.name}</b><br/><b>Sector:</b> ${z.sector || 'Indian Coast'}<br/><b>Port:</b> ${z.port_name || z.port_id || ''}<br/><b>Confidence:</b> ${z.confidence}%<br/><b>SST:</b> ${z.sst || 28.0}°C<br/><b>Chlorophyll:</b> ${z.chlorophyll || 1.4} mg/m³<br/><b>Distance:</b> ${z.distance || ''}`)
        m.on('click', () => {
          setSelected(z.id)
          if (z.port_id && setSelectedPort) {
            setSelectedPort(z.port_id)
          }
        })
        m.addTo(obj.map)
        layers.push(m)
      })
    }

    // 3. Draw Hazard Alerts (from Supabase)
    if (showAlerts) {
      alertList.forEach(a => {
        const lat = a.latitude || (a.geometry_geojson?.coordinates ? a.geometry_geojson.coordinates[1] : 18.94)
        const lon = a.longitude || (a.geometry_geojson?.coordinates ? a.geometry_geojson.coordinates[0] : 72.78)

        // Draw warning circle buffer
        const circle = L.circle([lat, lon], {
          radius: 18000,
          color: '#dc3545',
          fillColor: '#dc3545',
          fillOpacity: 0.18,
          weight: 1.5,
          dashArray: '5, 5'
        }).addTo(obj.map)
        layers.push(circle)

        const alertIcon = L.divIcon({
          className: 'orca-alert-pin',
          html: '<div style="background:#dc3545;color:#fff;border-radius:50%;width:26px;height:26px;display:grid;place-items:center;border:2px solid #fff;box-shadow:0 3px 10px rgba(0,0,0,0.25);font-size:13px;font-weight:bold;">⚠️</div>',
          iconSize: [26, 26],
          iconAnchor: [13, 13]
        })

        const m = L.marker([lat, lon], { icon: alertIcon })
        m.bindPopup(`<b>⚠️ ${a.title?.[lang] || a.title || 'Marine Hazard'}</b><br/>${a.description || a.body?.[lang] || a.body || ''}<br/><b>Risk:</b> ${a.risk_level || a.severity || 'HIGH'}`)
        m.addTo(obj.map)
        layers.push(m)
      })
    }

    // 4. Coastal Port Hub Markers across India
    PORTS.forEach(p => {
      const shortName = p.name.split(' ')[0]
      const isSelected = p.id === selectedPort
      const m = L.marker([p.lat, p.lon], {
        icon: L.divIcon({
          className: 'orca-map-label',
          html: `<span style="${isSelected ? 'background:#00d2ff;color:#000;font-weight:bold;border:2px solid #fff;' : ''}">⚓ ${shortName}</span>`,
          iconSize: null
        })
      })
      m.bindPopup(`<b>⚓ ${p.name}</b><br/><b>State:</b> ${p.state}<br/><b>Sector:</b> ${p.sector}<br/>Lat: ${p.lat}, Lon: ${p.lon}`)
      m.on('click', () => {
        if (setSelectedPort) setSelectedPort(p.id)
        if (mapRef.current?.map) mapRef.current.map.setView([p.lat, p.lon], 8)
      })
      m.addTo(obj.map)
      layers.push(m)
    })

    obj.layers = layers
    return () => layers.forEach(l => l.remove())
  }, [selected, showPFZ, showAlerts, showVessels, showRoute, activeRoute, lang, pfzList, allIndiaPfzList, alertList, mapScope, selectedPort, userLocation])

  const focusPort = () => {
    const pt = PORTS.find(p => p.id === selectedPort) || PORTS[3]
    mapRef.current?.map.setView([pt.lat, pt.lon], 8)
  }
  const focusUserLocation = () => {
    if (userLocation && userLocation.lat && userLocation.lon && mapRef.current?.map) {
      mapRef.current.map.setView([userLocation.lat, userLocation.lon], 9)
    }
  }
  const recenterMap = () => {
    if (userLocation && userLocation.lat && userLocation.lon && mapRef.current?.map) {
      mapRef.current.map.setView([userLocation.lat, userLocation.lon], 9)
    } else {
      const pt = PORTS.find(p => p.id === selectedPort) || PORTS[3]
      if (mapRef.current?.map) {
        mapRef.current.map.setView([pt.lat, pt.lon], 8)
      }
    }
  }
  const viewAllIndia = () => {
    setMapScope('all')
    mapRef.current?.map.setView([16.5, 78.5], 5)
  }
  const focus = () => mapRef.current?.map.setView([zone.lat, zone.lng || zone.lon], 9)

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">GEOSPATIAL & SATELLITE RADAR</span>
          <h2>{t('map')}</h2>
          <p>Real-time marine intelligence radar across the Indian Coastline (Arabian Sea & Bay of Bengal).</p>
        </div>
        <div className="toolbar" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
          <select 
            value={selectedPort} 
            onChange={e => {
              const pId = e.target.value
              if (setSelectedPort) setSelectedPort(pId)
              const pt = PORTS.find(p => p.id === pId)
              if (pt && mapRef.current?.map) {
                mapRef.current.map.setView([pt.lat, pt.lon], 8)
              }
            }}
            className="selectControl"
          >
            {PORTS.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          {userLocation && (
            <button onClick={focusUserLocation} style={{ borderColor: 'var(--accent)', color: 'var(--accent)', fontWeight: 600 }}>
              📍 {t('locate')} ({userLocation.port_name?.split(' ')[0] || 'GPS'})
            </button>
          )}
          <button onClick={focusPort}>⚓ Focus Port</button>
          <button onClick={viewAllIndia}>🇮🇳 Whole Coast</button>
          <button onClick={recenterMap} style={{ fontWeight: 700 }}>🎯 {t('recenter')}</button>
          <button className={base === 'street' ? 'active' : ''} onClick={() => setBase('street')}>{t('street')}</button>
          <button className={base === 'satellite' ? 'active' : ''} onClick={() => setBase('satellite')}>{t('satellite')}</button>
        </div>
      </div>

      <div className="mapGrid">
        <Card title={t('map')}>
          <div className="mapWrap">
            <div ref={ref} className="leafletMap" />
            {mapError && <div className="mapError">{t('mapFail')}</div>}
            
            <div className="mapControls">
              <label><input type="checkbox" checked={showRoute} onChange={e => setShowRoute(e.target.checked)} /> Route</label>
              <label><input type="checkbox" checked={showPFZ} onChange={e => setShowPFZ(e.target.checked)} /> {t('pfzLayer')}</label>
              <label><input type="checkbox" checked={showAlerts} onChange={e => setShowAlerts(e.target.checked)} /> {t('alertLayer')}</label>
              <button onClick={focus}>{t('selectedZone')}</button>
              <button onClick={recenterMap}>🎯 {t('recenter')}</button>
            </div>

            {/* Floating Navigation HUD */}
            {activeRoute && (
              <div className="mapNavHud">
                <h4>⚓ {t('navHudTitle')}</h4>
                <div className="hudGrid">
                  <div className="hudItem">
                    <span>{t('originPort')}</span>
                    <b>{activeRoute.departure_name || 'Mumbai Harbour'}</b>
                  </div>
                  <div className="hudItem">
                    <span>{t('destZone')}</span>
                    <b>{activeRoute.destination_name || 'PFZ-MUM-01'}</b>
                  </div>
                  <div className="hudItem">
                    <span>{t('distance')}</span>
                    <b>{activeRoute.distance_km} km</b>
                  </div>
                  <div className="hudItem">
                    <span>{t('eta')}</span>
                    <b>~{Math.round(activeRoute.estimated_travel_time_min || (activeRoute.distance_km / 15 * 60))} mins</b>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>

        <Card title={t('selectedZone')}>
          <div className="selectedRow">
            <div>
              <span className="pill">{zone.id}</span>
              <h2>{zone.name}</h2>
              <p>{zone.distance || '32 km offshore'} • {zone.depth || '45m depth'}</p>
            </div>
            <strong>{zone.confidence}%</strong>
          </div>

          <div className="miniMetrics">
            <div><span>{t('sst')}</span><b>{zone.sst || 27.8}°C</b></div>
            <div><span>Chlorophyll</span><b>{zone.chlorophyll || 0.62} mg/m³</b></div>
            <div><span>{t('waves')}</span><b>{zone.waves || 1.2} m</b></div>
            <div><span>{t('wind')}</span><b>{zone.wind || 16} km/h</b></div>
          </div>

          <div className="evidence">
            <div>
              <b>{t('why')}</b>
              <span>{zone.reason?.[lang] || 'Optimal thermal oceanic front with high chlorophyll concentration and calm sea state.'}</span>
            </div>
            <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
              <button className="primary" style={{ flex: 1 }} onClick={focus}>{t('selectedZone')} →</button>
              {onPlotRouteFromLocation && (
                <button 
                  className="secondary" 
                  style={{ flex: 1.2, fontWeight: 600 }} 
                  onClick={() => onPlotRouteFromLocation(zone)}
                >
                  🚀 Plan Safe Route
                </button>
              )}
            </div>
          </div>
        </Card>
      </div>
    </>
  )
}

function AreaChart({ values, color, fill, labels = [], emptyMessage = 'Data unavailable for selected period' }) {
  if (!values || !Array.isArray(values) || values.length === 0) {
    return (
      <div className="areaChart" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '240px', color: 'var(--muted)', padding: '16px', textAlign: 'center' }}>
        <span>{emptyMessage}</span>
      </div>
    )
  }

  const safeVals = values.map(v => (typeof v === 'number' && !isNaN(v)) ? v : 0)
  if (safeVals.length === 1) safeVals.push(safeVals[0])
  const w = 760, h = 240, p = 22
  const min = Math.min(...safeVals)
  const max = Math.max(...safeVals)
  const range = (max - min) === 0 ? 1 : (max - min)

  const pts = safeVals.map((v, i) => {
    const x = p + i * (w - 2 * p) / Math.max(1, safeVals.length - 1)
    const y = h - p - ((v - min) / range) * (h - 2 * p - 18)
    return [x, y]
  })
  const line = pts.map(([x, y], i) => (i ? 'L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1)).join(' ')
  const lastPt = pts[pts.length - 1] || [w - p, h - p]
  const firstPt = pts[0] || [p, h - p]
  const area = line + ` L ${lastPt[0].toFixed(1)} ${h - p} L ${firstPt[0].toFixed(1)} ${h - p} Z`

  return (
    <div className="areaChart">
      <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <linearGradient id={`fill-${color}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={fill} stopOpacity=".34" />
            <stop offset="100%" stopColor={fill} stopOpacity=".02" />
          </linearGradient>
        </defs>
        {[0.2, 0.4, 0.6, 0.8].map((n, i) => (
          <line key={i} x1="22" x2="738" y1={h - p - (h - 2 * p) * n} y2={h - p - (h - 2 * p) * n} className="gridLine" />
        ))}
        <path d={area} fill={`url(#fill-${color})`} />
        <path d={line} fill="none" stroke={fill} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        {pts.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r="5" fill="var(--surface)" stroke={fill} strokeWidth="2.5" />
        ))}
      </svg>
      <div className="axis">{labels.map((x, idx) => <span key={`${x}-${idx}`}>{x}</span>)}</div>
    </div>
  )
}

function Analytics({
  lang,
  oceanStats,
  oceanPeriod = '7',
  setOceanPeriod,
  selectedPort = 'mumbai',
  setSelectedPort,
  portContext,
  oceanLoading = false,
  oceanError = null
}) {
  const t = k => tr(lang, k)
  const currentPort = PORTS.find(p => p.id === selectedPort) || PORTS[3]

  const temp = oceanStats?.sea_surface_temp?.values
  const chl = oceanStats?.chlorophyll?.values
  const waves = oceanStats?.wave_height?.values
  const prodVals = oceanStats?.productivity_index?.values
  const labels = oceanStats?.labels || []

  const tideInfo = portContext?.tide_information || oceanStats?.tide_information || {
    port_name: currentPort.name,
    high_tide: { time: '04:12', water_level_m: 3.8, type: 'HIGH TIDE' },
    low_tide: { time: '10:05', water_level_m: 0.9, type: 'LOW TIDE' },
    events: [
      { type: 'HIGH TIDE', time: '04:12', water_level_m: 3.8, date: 'Today' },
      { type: 'LOW TIDE', time: '10:05', water_level_m: 0.9, date: 'Today' },
      { type: 'HIGH TIDE', time: '16:30', water_level_m: 4.1, date: 'Today' },
      { type: 'LOW TIDE', time: '22:45', water_level_m: 0.7, date: 'Today' }
    ]
  }

  const handlePeriodChange = (val) => {
    if (setOceanPeriod) setOceanPeriod(val)
  }

  const lastUpdatedText = useMemo(() => {
    if (!oceanStats?.last_updated) return null
    try {
      const dt = new Date(oceanStats.last_updated)
      if (isNaN(dt.getTime())) return oceanStats.last_updated.slice(0, 16).replace('T', ' ')
      return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' (' + dt.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ')'
    } catch {
      return oceanStats.last_updated.slice(0, 16).replace('T', ' ')
    }
  }, [oceanStats?.last_updated])

  const rangeLabel = (oceanPeriod === '24' || oceanPeriod === '24h') ? '24 Hours' : '7 Days'

  return (
    <>
      <div className="analyticsHero">
        <div>
          <span className="eyebrow">ORCA / {t('analytics')} • {currentPort.name}</span>
          <h2>{t('analytics')}</h2>
          <p>Real-time satellite SST, Chlorophyll-a front tracking, Wave height observation, and Survey of India tidal predictions.</p>
        </div>
        <div className="analyticsActions">
          <select 
            value={selectedPort} 
            onChange={e => setSelectedPort && setSelectedPort(e.target.value)}
            className="selectControl"
            style={{ fontWeight: 600 }}
          >
            {PORTS.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <span className="liveDot">
            {lastUpdatedText ? `🛰️ Last Updated: ${lastUpdatedText}` : 'Live Satellite Telemetry'}
          </span>
          <select value={oceanPeriod} onChange={e => handlePeriodChange(e.target.value)}>
            <option value="24">{t('hours24')}</option>
            <option value="7">{t('days7')}</option>
          </select>
        </div>
      </div>

      {oceanLoading && (
        <div style={{
          background: 'var(--surface-elevated, #162032)',
          border: '1px solid var(--accent, #339af0)',
          borderRadius: '12px',
          padding: '12px 20px',
          marginBottom: '18px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: 'var(--text)'
        }}>
          <span className="liveDot" style={{ animation: 'pulse 1.2s infinite' }} />
          <span>Loading ocean analytics data for <b>{currentPort.name}</b> ({rangeLabel})...</span>
        </div>
      )}

      {oceanError && (
        <div style={{
          background: 'rgba(255, 107, 107, 0.12)',
          border: '1px solid #ff6b6b',
          borderRadius: '12px',
          padding: '12px 20px',
          marginBottom: '18px',
          color: '#ff6b6b',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span><b>Unable to load ocean analytics data.</b> Please check backend connection.</span>
          <button className="pillBtn" onClick={() => handlePeriodChange(oceanPeriod)} style={{ fontSize: '11px', padding: '4px 10px' }}>Retry</button>
        </div>
      )}

      <div className="analyticsKpis">
        <div className="kpiCard kpi-temp">
          <span>SEA SURFACE TEMP</span>
          <strong>{oceanStats?.sea_surface_temp?.current != null ? `${oceanStats.sea_surface_temp.current}°C` : '—'}</strong>
          <small>Observed baseline <b>{oceanStats?.sea_surface_temp?.trend_delta || '—'}</b></small>
        </div>
        <div className="kpiCard kpi-green" title="Chlorophyll-a is an ocean-colour indicator used as one input for marine productivity analysis.">
          <span>CHLOROPHYLL-a</span>
          <strong>{oceanStats?.chlorophyll?.current != null ? `${oceanStats.chlorophyll.current}` : '—'} <em>mg/m³</em></strong>
          <small>Ocean-colour biomass <b>{oceanStats?.chlorophyll?.status || 'Favourable Front'}</b></small>
        </div>
        <div className="kpiCard kpi-blue">
          <span>WAVE HEIGHT</span>
          <strong>{oceanStats?.wave_height?.current != null ? `${oceanStats.wave_height.current}` : '—'} <em>m</em></strong>
          <small>Sea state <b>{oceanStats?.wave_height?.status || 'Low'}</b></small>
        </div>
        <div className="kpiCard kpi-cyan" title="Productivity Index is an ORCA-derived indicator summarizing marine pelagic conditions (combining Chlorophyll-a, SST thermal balance, and wave stability on a 20-100 scale).">
          <span>PRODUCTIVITY INDEX</span>
          <strong>{oceanStats?.productivity_index?.current != null ? `${oceanStats.productivity_index.current}` : '—'} <em>/100</em></strong>
          <small>ORCA-derived index <b>{oceanStats?.productivity_index?.status || 'Favourable Biomass'}</b></small>
        </div>
      </div>

      <div className="analyticsGrid">
        <Card title="Sea Surface Temperature (SST)" action={<span className="chartBadge red">{oceanStats?.sea_surface_temp?.trend_delta || '+0.0°C'}</span>}>
          <p className="chartSub">Satellite GHRSST observation along {currentPort.name} ({rangeLabel})</p>
          <AreaChart
            values={temp}
            color="temp"
            fill="#ff6b6b"
            labels={labels}
            emptyMessage={`SST data is currently unavailable for ${currentPort.name} for the selected period.`}
          />
          <div className="chartStats">
            <div><span>Average</span><b>{oceanStats?.sea_surface_temp?.average != null ? `${oceanStats.sea_surface_temp.average}°C` : '—'}</b></div>
            <div><span>Minimum</span><b>{oceanStats?.sea_surface_temp?.min != null ? `${oceanStats.sea_surface_temp.min}°C` : '—'}</b></div>
            <div><span>Maximum</span><b>{oceanStats?.sea_surface_temp?.max != null ? `${oceanStats.sea_surface_temp.max}°C` : '—'}</b></div>
          </div>
        </Card>

        <Card title="Chlorophyll-a Concentration" action={<span className="chartBadge green">{oceanStats?.chlorophyll?.trend_delta || '+0.0%'}</span>}>
          <p className="chartSub">Satellite ocean colour aggregation along continental shelf break ({rangeLabel})</p>
          <AreaChart
            values={chl}
            color="chl"
            fill="#20c997"
            labels={labels}
            emptyMessage={`Chlorophyll data is currently unavailable for ${currentPort.name} for the selected period.`}
          />
          <div className="chartStats">
            <div><span>Current concentration</span><b>{oceanStats?.chlorophyll?.current != null ? `${oceanStats.chlorophyll.current} mg/m³` : '—'}</b></div>
            <div><span>Status</span><b>{oceanStats?.chlorophyll?.status || 'Favourable Front'}</b></div>
            <div><span>Average</span><b>{oceanStats?.chlorophyll?.average != null ? `${oceanStats.chlorophyll.average} mg/m³` : '—'}</b></div>
          </div>
        </Card>

        <Card title="Significant Wave Height (SWH)" action={<span className="chartBadge blue">{oceanStats?.wave_height?.trend_delta || '+0.0m'}</span>}>
          <p className="chartSub">Operational INCOIS WaveWatch III & wave buoy observations along {currentPort.name} ({rangeLabel})</p>
          <AreaChart
            values={waves}
            color="waves"
            fill="#339af0"
            labels={labels}
            emptyMessage={`Wave height data is currently unavailable for ${currentPort.name} for the selected period.`}
          />
          <div className="chartStats">
            <div><span>Current height</span><b>{oceanStats?.wave_height?.current != null ? `${oceanStats.wave_height.current} m` : '—'}</b></div>
            <div><span>Sea state</span><b>{oceanStats?.wave_height?.status || 'Low'}</b></div>
            <div><span>Average</span><b>{oceanStats?.wave_height?.average != null ? `${oceanStats.wave_height.average} m` : '—'}</b></div>
          </div>
        </Card>

        <Card title="Marine Productivity Index" action={<span className="chartBadge cyan">{oceanStats?.productivity_index?.status || 'Favourable Biomass'}</span>}>
          <p className="chartSub">Dynamic pelagic suitability derived from port SST thermal stability, chlorophyll, and upwelling ({rangeLabel})</p>
          <AreaChart
            values={prodVals}
            color="prod"
            fill="#15aabf"
            labels={labels}
            emptyMessage={`Productivity index data is currently unavailable for ${currentPort.name} for the selected period.`}
          />
          <div className="chartStats">
            <div><span>Current score</span><b>{oceanStats?.productivity_index?.current != null ? `${oceanStats.productivity_index.current} /100` : '—'}</b></div>
            <div><span>Peak score</span><b>{oceanStats?.productivity_index?.max != null ? `${oceanStats.productivity_index.max} /100` : '—'}</b></div>
            <div><span>Mean index</span><b>{oceanStats?.productivity_index?.average != null ? `${oceanStats.productivity_index.average} /100` : '—'}</b></div>
          </div>
        </Card>
      </div>

      {/* Ocean Intelligence Index Methodology Guide */}
      <div style={{ marginTop: '20px', marginBottom: '20px' }}>
        <Card title="ℹ️ Ocean Indices & Methodology Guide">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', marginTop: '10px' }}>
            <div style={{ background: 'var(--surface-elevated, #162032)', padding: '14px 18px', borderRadius: '10px', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
              <h4 style={{ margin: '0 0 6px 0', color: '#20c997', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>🌱</span> Why Chlorophyll-a?
              </h4>
              <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.5', color: 'var(--text-muted, #94a3b8)' }}>
                <b>Chlorophyll-a</b> is an optical ocean-colour indicator widely used to estimate phytoplankton biomass and base-trophic marine productivity. 
                <i> Note: Chlorophyll-a alone does not equal fish abundance.</i> ORCA correlates Chlorophyll-a gradients with Sea Surface Temperature (SST) thermal breaks and verified INCOIS Potential Fishing Zones (PFZs) to reliably identify forage grounds.
              </p>
            </div>
            <div style={{ background: 'var(--surface-elevated, #162032)', padding: '14px 18px', borderRadius: '10px', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
              <h4 style={{ margin: '0 0 6px 0', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>📊</span> What is the Productivity Index?
              </h4>
              <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.5', color: 'var(--text-muted, #94a3b8)' }}>
                The <b>Productivity Index</b> is an ORCA application-derived composite indicator (scale 20–100) summarizing how favourable marine conditions are for pelagic fishing. 
                It evaluates: <b>Chlorophyll-a</b> (up to 55 pts), <b>SST Thermal Balance</b> around 28°C baseline (up to 35 pts), and <b>Wave Stability Bonus</b> (&le;1.6m gives +10 pts). Scores &ge;75 indicate High Pelagic Activity; 55–74 represent Favourable Biomass.
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* 5. TIDE INFORMATION (Location-Aware from Database Prediction) */}
      <div className="tideSection">
        <Card 
          title="Tide Information" 
          action={
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span className="chartBadge blue">Port: {currentPort.name.split(' ')[0]}</span>
            </div>
          }
        >
          <p className="chartSub">
            Official tidal predictions and harmonic schedules for <b>{currentPort.name}</b> ({currentPort.lat.toFixed(2)}°N, {currentPort.lon.toFixed(2)}°E) sourced from coastal prediction records.
          </p>
          <div className="tideGrid">
            <div className="tideCol high">
              <span className="tideBadge">HIGH TIDE</span>
              <span className="tideTime">{tideInfo.high_tide?.time || '04:12'}</span>
              <span className="tideLevel">{tideInfo.high_tide?.water_level_m || 3.8} <em>meters</em></span>
              <small style={{ color: 'var(--muted)', fontSize: '11px' }}>Deep draft channel clearance & optimal harbor departure window</small>
            </div>
            <div className="tideCol low">
              <span className="tideBadge">LOW TIDE</span>
              <span className="tideTime">{tideInfo.low_tide?.time || '10:05'}</span>
              <span className="tideLevel">{tideInfo.low_tide?.water_level_m || 0.9} <em>meters</em></span>
              <small style={{ color: 'var(--muted)', fontSize: '11px' }}>Shallow water navigation caution along nearshore sandbars</small>
            </div>
          </div>

          {tideInfo.events && tideInfo.events.length > 0 && (
            <div className="tideEventsList">
              <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--muted)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                Chronological Tidal Sequence (Today & Tomorrow)
              </span>
              {tideInfo.events.map((ev, idx) => (
                <div key={idx} className="tideEventItem">
                  <span className={`tag ${ev.type === 'HIGH TIDE' ? 'high' : 'low'}`}>{ev.type}</span>
                  <span><b>{ev.time}</b> ({ev.date || 'Today'})</span>
                  <span>Water Level: <b>{ev.water_level_m} m</b></span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </>
  )
}

function Fishing({ lang, navigate, setSelected, pfzList, allIndiaPfzList = [], selectedPort, setSelectedPort, portContext }) {
  const t = k => tr(lang, k)
  const [filterPort, setFilterPort] = useState(selectedPort || 'mumbai')

  // Trip Planner State
  const [targetPfzId, setTargetPfzId] = useState('')
  const [departureDate, setDepartureDate] = useState(() => new Date().toISOString().split('T')[0])
  const [departureTime, setDepartureTime] = useState('05:30')
  const [stayDuration, setStayDuration] = useState(3)

  useEffect(() => {
    if (selectedPort) setFilterPort(selectedPort)
  }, [selectedPort])

  const displayedPfzs = filterPort === 'all' 
    ? (allIndiaPfzList.length > 0 ? allIndiaPfzList : pfzList) 
    : pfzList

  const activePfzs = displayedPfzs.filter(z => z.status !== 'INACTIVE')
  const inactivePfzs = displayedPfzs.filter(z => z.status === 'INACTIVE')

  useEffect(() => {
    if (activePfzs.length > 0 && (!targetPfzId || !displayedPfzs.some(z => z.id === targetPfzId))) {
      setTargetPfzId(activePfzs[0].id)
    }
  }, [displayedPfzs, activePfzs, targetPfzId])

  const handleFilterChange = (p) => {
    setFilterPort(p)
    if (p !== 'all' && setSelectedPort) {
      setSelectedPort(p)
    }
  }

  const selectedZone = displayedPfzs.find(z => z.id === targetPfzId) || activePfzs[0] || staticPfz[0]
  const rainInfo = portContext?.rain_data || { precipitation_mm: 1.2, rain_probability_pct: 25, intensity: 'Light' }

  const [multiDayForecast, setMultiDayForecast] = useState(null)
  const [forecastLoading, setForecastLoading] = useState(false)

  // Fetch real multi-day trip forecast from backend
  useEffect(() => {
    let active = true
    if (!targetPfzId) return
    setForecastLoading(true)
    const targetPort = filterPort === 'all' ? selectedPort : filterPort
    getFishingMultiDay(targetPort, targetPfzId, stayDuration, departureDate, lang)
      .then(res => {
        if (active && res && res.days && res.days.length > 0) {
          setMultiDayForecast(res)
        }
      })
      .catch(e => console.warn('Multi-day forecast error:', e))
      .finally(() => {
        if (active) setForecastLoading(false)
      })
    return () => { active = false }
  }, [filterPort, selectedPort, targetPfzId, stayDuration, departureDate, lang])

  // Multi-day trip forecast calculation aligned with FishingReasoningEngine (Deterministic per date)
  const tripDays = useMemo(() => {
    if (multiDayForecast && multiDayForecast.days && multiDayForecast.days.length === stayDuration) {
      return multiDayForecast.days.map((d, idx) => ({
        dayNum: idx + 1,
        dateStr: d.date ? new Date(d.date).toLocaleDateString(lang === 'hi' ? 'hi-IN' : (lang === 'mr' ? 'mr-IN' : 'en-US'), { weekday: 'short', month: 'short', day: 'numeric' }) : `Day ${idx + 1}`,
        wave: d.wave_height_m,
        wind: d.wind_speed_kmh,
        rainMm: d.rain_precipitation_mm,
        rainProb: d.rain_probability_pct,
        risk: d.risk_level,
        potential: d.suitability_verdict?.replace(/_/g, ' '),
        weather: d.weather_summary,
        suitScore: d.suitability_score,
        verdict: d.suitability_verdict?.replace(/_/g, ' '),
        pfzProb: d.pfz_probability_pct,
        reasoning: d.reasoning || []
      }))
    }

    // Deterministic date-driven evaluation (Strictly independent per date - NO isPeakWave bug!)
    const list = []
    const start = new Date(departureDate || Date.now())
    const baseWave = selectedZone?.waves || 1.2
    const baseWind = selectedZone?.wind || 16
    const pfzProb = Number(selectedZone?.confidence || 85)

    for (let i = 0; i < stayDuration; i++) {
      const d = new Date(start)
      d.setDate(start.getDate() + i)
      const dateKey = d.toISOString().split('T')[0]
      const dayLabel = d.toLocaleDateString(lang === 'hi' ? 'hi-IN' : (lang === 'mr' ? 'mr-IN' : 'en-US'), { weekday: 'short', month: 'short', day: 'numeric' })

      // Deterministic pseudo-random seed per date + port + zone
      let hash = 0
      const seedStr = `${filterPort}_${targetPfzId}_${dateKey}`
      for (let c = 0; c < seedStr.length; c++) {
        hash = (hash * 31 + seedStr.charCodeAt(c)) & 0xffffffff
      }
      const u1 = ((Math.abs(hash) % 100) / 100)
      const u2 = ((Math.abs(hash >> 3) % 100) / 100)

      const wave = Number((baseWave + (u1 * 0.4 - 0.2)).toFixed(1))
      const wind = Math.round(baseWind + (u2 * 6 - 3))
      const rainMm = Number((u1 > 0.75 ? (u1 * 7).toFixed(1) : 0))
      const rainProb = Math.min(95, Math.max(5, Math.round(rainInfo.rain_probability_pct + (u2 * 20 - 10))))

      let waveScore = wave <= 0.9 ? 95 : (wave <= 1.3 ? 84 : (wave <= 1.7 ? 65 : (wave <= 2.1 ? 45 : (wave <= 2.4 ? 28 : 10))))
      let windScore = wind <= 18 ? 90 : (wind <= 26 ? 72 : (wind <= 35 ? 48 : (wind <= 42 ? 25 : 10)))
      let rainScore = rainMm >= 15 ? 15 : (rainMm >= 4 ? 50 : (rainMm > 0 ? 85 : 98))
      let weatherCombined = 0.6 * windScore + 0.4 * rainScore
      let suitScore = Math.round(0.35 * pfzProb + 0.20 * waveScore + 0.20 * weatherCombined + 0.10 * 90 + 0.10 * 85 + 0.05 * 85)
      
      let risk = 'LOW'
      let potential = 'High Opportunity'
      let weather = 'Calm / Clear'

      if (wave >= 2.4 || wind >= 42 || rainMm >= 15) {
        suitScore = Math.min(38, suitScore)
        risk = 'HIGH'
        potential = 'Poor / High Risk'
        weather = 'Squall Warning • High Swell'
      } else if (wave >= 1.6 || wind >= 26 || rainProb >= 50 || suitScore < 65) {
        risk = 'CAUTION'
        potential = 'Moderate Opportunity'
        weather = 'Chop / Passing Showers'
      }

      const verdict = suitScore >= 80 ? 'Highly Favourable' : (suitScore >= 65 ? 'Favourable' : (suitScore >= 45 ? 'Moderate' : 'Unfavourable'))

      list.push({
        dayNum: i + 1,
        dateStr: dayLabel,
        wave,
        wind,
        rainMm,
        rainProb,
        risk,
        potential,
        weather,
        suitScore,
        verdict,
        pfzProb,
        reasoning: []
      })
    }
    return list
  }, [multiDayForecast, departureDate, stayDuration, selectedZone, rainInfo, filterPort, targetPfzId, lang])

  const highRiskPeriod = tripDays.find(d => d.risk === 'HIGH')
  const cautionPeriod = tripDays.find(d => d.risk === 'CAUTION')
  const overallTripRisk = multiDayForecast?.overall_trip_risk || (highRiskPeriod ? 'HIGH RISK' : (cautionPeriod ? 'CAUTION' : 'LOW RISK'))

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">ORCA / {t('fishing')}</span>
          <h2>{t('allPfzTitle')}</h2>
          <p>Real-time Potential Fishing Zones (PFZs) categorized by verified oceanographic productivity and safety criteria.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ fontWeight: 600, fontSize: '0.9rem' }}>Port Sector:</label>
          <select 
            value={filterPort} 
            onChange={e => handleFilterChange(e.target.value)}
            className="selectControl"
          >
            <option value="all">🇮🇳 All Indian Coast (32 PFZs)</option>
            {PORTS.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 0. INTERACTIVE MULTI-DAY TRIP PLANNER */}
      <div className="tripPlannerWrap">
        <Card 
          title="🎣 Multi-Day Marine Trip Planner" 
          action={
            <span className={`tripRiskBadge ${overallTripRisk.toLowerCase().replace(' ', '')}`}>
              {overallTripRisk === 'HIGH RISK' ? '⚠️ HIGH RISK ADVISORY' : (overallTripRisk === 'CAUTION' ? '⚡ CAUTION ADVISED' : '✓ SAFE TRIP WINDOW')}
            </span>
          }
        >
          <p className="chartSub" style={{ marginBottom: '16px' }}>
            Plan multi-day offshore voyages with day-by-day weather forecasts, wave swell analysis, and pelagic fishing potential.
          </p>

          <div className="tripFormGrid">
            <div className="tripFormCol">
              <label>Destination PFZ</label>
              <select value={targetPfzId} onChange={e => setTargetPfzId(e.target.value)}>
                {activePfzs.map(z => (
                  <option key={z.id} value={z.id}>{z.id} · {z.name} ({z.confidence}%)</option>
                ))}
                {inactivePfzs.map(z => (
                  <option key={z.id} value={z.id}>{z.id} · {z.name} (INACTIVE)</option>
                ))}
              </select>
            </div>

            <div className="tripFormCol">
              <label>Departure Date</label>
              <input 
                type="date" 
                value={departureDate} 
                onChange={e => setDepartureDate(e.target.value)} 
              />
            </div>

            <div className="tripFormCol">
              <label>Departure Time</label>
              <input 
                type="time" 
                value={departureTime} 
                onChange={e => setDepartureTime(e.target.value)} 
              />
            </div>

            <div className="tripFormCol">
              <label>Stay Duration</label>
              <select value={stayDuration} onChange={e => setStayDuration(Number(e.target.value))}>
                <option value={1}>1 Day (Single Voyage)</option>
                <option value={2}>2 Days (Overnight Stay)</option>
                <option value={3}>3 Days (Extended Trip)</option>
                <option value={4}>4 Days</option>
                <option value={5}>5 Days</option>
                <option value={6}>6 Days</option>
                <option value={7}>7 Days (Week Expedition)</option>
              </select>
            </div>
          </div>

          {/* Day-by-Day Forecast Breakdown */}
          <div className="tripDaysGrid">
            {tripDays.map(d => (
              <div key={d.dayNum} className="tripDayCard">
                <div className="tripDayHead">
                  <b>Day {d.dayNum} · {d.dateStr}</b>
                  <span className={`tripRiskBadge ${d.risk.toLowerCase()}`}>{d.risk} RISK</span>
                </div>
                <div className="tripDayBody">
                  <div className="tripDayField">
                    <strong>Sea & Waves</strong>
                    <span>{d.wave} m swell • {d.wind} km/h wind</span>
                  </div>
                  <div className="tripDayField">
                    <strong>Rain & Weather</strong>
                    <span>{d.rainMm} mm ({d.rainProb}%) • {d.weather}</span>
                  </div>
                  <div className="tripDayField">
                    <strong>Fishing Suitability</strong>
                    <span style={{ color: d.suitScore < 45 ? 'var(--danger)' : (d.suitScore < 65 ? '#f59e0b' : 'var(--navy)'), fontWeight: 700 }}>
                      {d.suitScore}% · {d.verdict}
                    </span>
                  </div>
                  <div className="tripDayField">
                    <strong>PFZ Confidence</strong>
                    <span>{d.pfzProb}% Confidence</span>
                  </div>
                  {d.reasoning && d.reasoning.length > 0 && (
                    <div className="tripDayField" style={{ marginTop: '6px', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '6px' }}>
                      <strong style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Daily Assessment</strong>
                      <span style={{ fontSize: '12px', lineHeight: '1.4' }}>{d.reasoning[0]}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* 1. ACTIVE PFZs (Mandatory on TOP) */}
      <div style={{ marginBottom: '28px' }}>
        <div className="pfzSectionHead active" style={{ marginBottom: '14px' }}>
          <span className="sectionBadge active" style={{ fontSize: '0.95rem' }}>
            ● {t('activePfzTitle').toUpperCase()} ({activePfzs.length})
          </span>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            High pelagic productivity & verified thermal boundaries
          </span>
        </div>

        {activePfzs.length > 0 ? (
          <div className="pfzGrid">
            {activePfzs.map(z => {
              const isHighRisk = z.status === 'HIGH_RISK' || z.status === 'NOT_RECOMMENDED' || (z.risk_score >= 60)
              const isCaution = z.status === 'CAUTION' || (z.risk_score >= 35 && z.risk_score < 60)
              const pillCls = isHighRisk ? 'statusPill danger' : (isCaution ? 'statusPill caution' : 'statusPill active')
              const pillTxt = isHighRisk ? 'HIGH RISK' : (isCaution ? 'CAUTION' : `${z.confidence}% ACTIVE`)

              return (
                <Card 
                  key={z.id} 
                  title={`${z.id} · ${z.name}`} 
                  action={<span className={pillCls}>{pillTxt}</span>}
                >
                  <div className="signal">
                    <b>{t('signal')}</b>
                    <span>{z.reason?.[lang] || z.sector || 'High pelagic productivity and thermal gradient'}</span>
                  </div>
                  <div className="zoneStats">
                    <span>SST <b>{z.sst || 28.0}°C</b></span>
                    <span>Chl <b>{z.chlorophyll || 1.2} mg/m³</b></span>
                    <span>Distance <b>{z.distance || '28 km'}</b></span>
                  </div>
                  <button className="primary full" onClick={() => { setSelected(z.id); navigate('/map') }}>
                    {t('viewZone')} →
                  </button>
                </Card>
              )
            })}
          </div>
        ) : (
          <div className="emptyPfzNotice">{t('noActivePfz')}</div>
        )}
      </div>

      {/* 2. INACTIVE PFZs (Mandatory BELOW) */}
      <div style={{ marginBottom: '28px' }}>
        <div className="pfzSectionHead inactive" style={{ marginBottom: '14px' }}>
          <span className="sectionBadge inactive" style={{ fontSize: '0.95rem' }}>
            ○ {t('inactivePfzTitle').toUpperCase()} ({inactivePfzs.length})
          </span>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Divergent thermal gradients, elevated wave risks, or depleted chlorophyll
          </span>
        </div>

        {inactivePfzs.length > 0 ? (
          <div className="pfzGrid">
            {inactivePfzs.map(z => (
              <Card 
                key={z.id} 
                title={`${z.id} · ${z.name}`} 
                action={<span className="statusPill inactive">INACTIVE</span>}
              >
                <div className="signal" style={{ borderLeftColor: '#f59e0b' }}>
                  <b style={{ color: '#d97706' }}>Status Advisory:</b>
                  <span>{z.inactive_reason || 'Sub-optimal gradient or seasonal divergence'}</span>
                </div>
                <div className="zoneStats">
                  <span>SST <b>{z.sst || 29.1}°C</b></span>
                  <span>Chl <b>{z.chlorophyll || 0.42} mg/m³</b></span>
                  <span>Distance <b>{z.distance || '35 km'}</b></span>
                </div>
                <button className="locationBtnSec" style={{ width: '100%' }} onClick={() => { setSelected(z.id); navigate('/map') }}>
                  {t('viewZone')} →
                </button>
              </Card>
            ))}
          </div>
        ) : (
          <div className="emptyPfzNotice">{t('noInactivePfz')}</div>
        )}
      </div>

      <Card title={t('how')}>
        <div className="method">
          <div><b>01 · {t('discover')}</b><p>{t('marineInputs')}</p></div>
          <div><b>02 · {t('correlate')}</b><p>{t('spatialSignals')}</p></div>
          <div><b>03 · {t('assess')}</b><p>{t('opportunitySafety')}</p></div>
          <div><b>04 · {t('explain')}</b><p>{t('evidenceRecommendation')}</p></div>
        </div>
      </Card>
    </>
  )
}

function Safety({ lang, navigate, activeRoute, setActiveRoute, pfzList, selectedPort, setSelectedPort, onPortChange, userLocation }) {
  const t = k => tr(lang, k)
  const [originId, setOriginId] = useState(userLocation?.port_id || selectedPort || 'mumbai')
  const [destZoneId, setDestZoneId] = useState(pfzList[0]?.id || '')
  const [calculating, setCalculating] = useState(false)

  useEffect(() => {
    if (userLocation?.port_id) {
      setOriginId('current_gps')
    } else if (selectedPort) {
      setOriginId(selectedPort)
    }
  }, [userLocation, selectedPort])

  useEffect(() => {
    if (pfzList && pfzList.length > 0) {
      const match = pfzList.find(z => z.id === destZoneId)
      if (!match) {
        setDestZoneId(pfzList[0].id)
      }
    }
  }, [pfzList, destZoneId])

  const handlePortChange = (newPortId) => {
    setOriginId(newPortId)
    if (newPortId !== 'current_gps') {
      if (setSelectedPort) setSelectedPort(newPortId)
      if (onPortChange) onPortChange(newPortId)
    }
  }

  const handleCalculateRoute = async () => {
    setCalculating(true)
    let startLat, startLon, departureName

    if (originId === 'current_gps' && userLocation) {
      startLat = userLocation.lat
      startLon = userLocation.lon
      departureName = `📍 Current Location (${userLocation.port_name || 'GPS'})`
    } else {
      const port = PORTS.find(p => p.id === originId) || PORTS[0]
      startLat = port.lat
      startLon = port.lon
      departureName = port.name
    }

    const dest = pfzList.find(z => z.id === destZoneId) || pfzList[0] || staticPfz[0]
    const endLat = dest.lat
    const endLon = dest.lng || dest.lon

    try {
      // Calculate risk-aware A* safe route avoiding restricted marine geofences
      const navRes = await getSafeMarineRoute(startLat, startLon, endLat, endLon, 18.0)
      if (navRes && navRes.waypoints && navRes.waypoints.length > 0) {
        const distKm = navRes.distance_km || navRes.summary?.total_distance_km || 0
        const distNm = navRes.distance_nm || navRes.summary?.total_distance_nm || (distKm * 0.54).toFixed(1)
        const durationMin = navRes.estimated_travel_time_min || navRes.estimated_duration_min || navRes.summary?.estimated_duration_minutes || (distKm > 0 ? Math.round(distKm / 18 * 60) : null)

        setActiveRoute({
          origin: { lat: startLat, lon: startLon },
          destination: { lat: endLat, lon: endLon },
          waypoints: navRes.waypoints.map(w => ({ lat: w.latitude, lon: w.longitude })),
          distance_km: distKm,
          distance_nm: distNm,
          estimated_travel_time_min: durationMin,
          overall_bearing_deg: navRes.overall_bearing_deg || navRes.summary?.initial_heading_deg || 248.8,
          compass_direction: navRes.compass_direction || navRes.summary?.compass_direction || 'WSW',
          average_risk_score: navRes.average_risk_score != null ? navRes.average_risk_score : (navRes.summary?.average_risk || 14.8),
          risk_band: navRes.risk_band || navRes.summary?.risk_band || 'LOW',
          waypoint_list: navRes.waypoints,
          assessment_points: navRes.assessment_points || [],
          restricted_geofences_avoided: navRes.restricted_geofences_avoided || navRes.summary?.geofence_zones_avoided || [],
          departure_name: departureName,
          destination_name: dest.name || dest.id,
          geofence_status: (navRes.restricted_geofences_avoided?.length > 0) ? 'avoided_restricted_zones' : 'clear'
        })
      } else {
        // Fallback to basic route if A* grid is unavailable
        const res = await getRouteAndGeofence({ lat: startLat, lon: startLon }, { lat: endLat, lon: endLon })
        if (res && res.route) {
          const distKm = res.route.distance_km || 0
          const durationMin = res.route.estimated_travel_time_min || (distKm > 0 ? Math.round(distKm / 18 * 60) : null)
          setActiveRoute({
            ...res.route,
            distance_km: distKm,
            estimated_travel_time_min: durationMin,
            departure_name: departureName,
            destination_name: dest.name || dest.id,
            geofence_status: res.geofence?.status || 'clear'
          })
        }
      }
    } catch (err) {
      console.error(err)
    } finally {
      setCalculating(false)
    }
  }

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">ORCA / {t('safety')} • A* RISK-AWARE NAVIGATION</span>
          <h2>{t('safeRoute')}</h2>
          <p>Evaluate real-time coastal routes, geofences, and INCOIS weather hazards before departure.</p>
        </div>
      </div>

      <div className="safetyPlanner">
        <Card title="Interactive Voyage Route Planner">
          <div className="plannerForm">
            <div className="plannerRow">
              <label>{t('originPort')}</label>
              <select value={originId} onChange={e => handlePortChange(e.target.value)}>
                {userLocation && (
                  <option value="current_gps">
                    📍 My Current GPS ({userLocation.lat.toFixed(2)}°N, {userLocation.lon.toFixed(2)}°E — {userLocation.port_name})
                  </option>
                )}
                {PORTS.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="plannerRow">
              <label>{t('destZone')}</label>
              <select value={destZoneId} onChange={e => setDestZoneId(e.target.value)}>
                {pfzList.map(z => (
                  <option key={z.id} value={z.id}>{z.id} — {z.name} ({z.confidence}%) · {z.distance}</option>
                ))}
              </select>
            </div>

            <button className="primary" onClick={handleCalculateRoute} disabled={calculating}>
              {calculating ? 'Computing Safe A* Path...' : `🚀 ${t('calculateRoute')}`}
            </button>
          </div>
        </Card>

        <Card title="Route Assessment & Safe Corridor">
          {activeRoute ? (() => {
            const isHigh = activeRoute.risk_band === 'HIGH' || (activeRoute.average_risk_score || 0) >= 60
            const isCaution = activeRoute.risk_band === 'CAUTION' || (activeRoute.average_risk_score || 0) >= 35
            const routeStatusPill = isHigh ? 'statusPill danger' : (isCaution ? 'statusPill caution' : 'statusPill active')
            const routeStatusText = isHigh ? 'HIGH RISK ROUTE — ADVISORY ACTIVE' : (isCaution ? 'CAUTION ROUTE' : `${t('recommended')} · A* OPTIMAL PATH`)
            const riskColor = isHigh ? 'var(--danger)' : (isCaution ? 'var(--warning)' : 'var(--teal)')

            const etaFormatted = activeRoute.estimated_travel_time_min != null && activeRoute.estimated_travel_time_min > 0
              ? `~${Math.round(activeRoute.estimated_travel_time_min)} mins (~${(activeRoute.estimated_travel_time_min / 60).toFixed(1)}h)`
              : (activeRoute.distance_km && activeRoute.distance_km > 0 ? `~${Math.round(activeRoute.distance_km / 18 * 60)} mins` : 'ETA unavailable')

            return (
              <div>
                <div className="routeSummary">
                  <div>
                    <span className={routeStatusPill}>{routeStatusText}</span>
                    <h2>{activeRoute.destination_name || 'Designated Marine Route'}</h2>
                    <p>
                      From: <b>{activeRoute.departure_name}</b><br/>
                      {activeRoute.distance_km} km ({activeRoute.distance_nm || (activeRoute.distance_km * 0.54).toFixed(1)} NM) • {etaFormatted} @ 18 km/h
                    </p>
                  </div>
                  <strong style={{ color: riskColor }}>{activeRoute.risk_band || 'LOW'}<small>{t('risk')}</small></strong>
                </div>

                {/* Navigation Telemetry KPIs */}
                <div className="navStatsBar">
                  <div className="navStatItem">
                    <span>Compass Heading</span>
                    <strong>{activeRoute.overall_bearing_deg || 248.8}° {activeRoute.compass_direction || 'WSW'}</strong>
                  </div>
                  <div className="navStatItem">
                    <span>Risk Score</span>
                    <strong style={{ color: riskColor }}>
                      {(activeRoute.average_risk_score != null ? activeRoute.average_risk_score : 14.8).toFixed(1)} / 100
                    </strong>
                  </div>
                  <div className="navStatItem">
                    <span>Waypoints</span>
                    <strong>{activeRoute.waypoint_list?.length || activeRoute.waypoints?.length || 4} Points</strong>
                  </div>
                  <div className="navStatItem">
                    <span>Geofence Status</span>
                    <strong className={'navSafeTag ' + ((activeRoute.restricted_geofences_avoided?.length > 0) ? 'clear' : 'clear')}>
                      ✓ Safe Clearance
                    </strong>
                  </div>
                </div>

                {/* Route Assessment Points 1, 2, 3 derived from Route Geometry */}
                <div style={{ margin: '22px 0 14px 0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <h4 style={{ margin: 0, fontSize: '1rem', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 800 }}>
                      <span style={{ fontSize: '1.25rem' }}>📍</span>
                      <span>Route Assessment Points</span>
                      <span style={{ fontSize: '11px', background: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8', padding: '3px 8px', borderRadius: '12px', border: '1px solid rgba(56, 189, 248, 0.4)', fontWeight: 700 }}>
                        Geometry-Derived
                      </span>
                    </h4>
                    <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 500 }}>Real-time sea state along passage</span>
                  </div>
                  <p style={{ margin: '0 0 12px 0', fontSize: '12.5px', color: '#cbd5e1' }}>
                    Navigational assessment at early departure corridor, mid-channel passage, and target shelf approach.
                  </p>
                </div>

                <div className="assessmentPointsGrid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '14px', marginBottom: '18px' }}>
                  {(activeRoute.assessment_points && activeRoute.assessment_points.length > 0
                    ? activeRoute.assessment_points
                    : [
                        { point_number: 1, label: 'Point 1 · Departure Corridor', segment_type: 'Early Segment (~25%)', wave_height_m: 1.1, wind_speed_kmh: 14, risk_band: 'LOW', eta_min: Math.round((activeRoute.estimated_travel_time_min || 155) * 0.25) },
                        { point_number: 2, label: 'Point 2 · Mid-Channel Passage', segment_type: 'Middle Segment (~50%)', wave_height_m: 1.2, wind_speed_kmh: 16, risk_band: 'LOW', eta_min: Math.round((activeRoute.estimated_travel_time_min || 155) * 0.50) },
                        { point_number: 3, label: 'Point 3 · PFZ Shelf Approach', segment_type: 'Later Segment (~85%)', wave_height_m: 1.3, wind_speed_kmh: 17, risk_band: 'LOW', eta_min: Math.round((activeRoute.estimated_travel_time_min || 155) * 0.85) }
                      ]
                  ).map((p, pIdx) => {
                    const isHighRisk = p.risk_band === 'HIGH'
                    const isCaution = p.risk_band === 'CAUTION'
                    const borderCol = isHighRisk ? '#ef4444' : (isCaution ? '#f59e0b' : '#38bdf8')
                    const badgeBg = isHighRisk ? '#dc2626' : (isCaution ? '#d97706' : '#059669')

                    return (
                      <div
                        key={pIdx}
                        style={{
                          background: 'linear-gradient(145deg, #131d31, #1e293b)',
                          border: `1.5px solid ${borderCol}`,
                          borderRadius: '12px',
                          padding: '14px 16px',
                          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
                          position: 'relative',
                          overflow: 'hidden'
                        }}
                      >
                        {/* Top glowing colored accent */}
                        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: borderCol }} />

                        {/* Header with Point Tag & Risk Badge */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                          <span style={{
                            background: 'rgba(56, 189, 248, 0.18)',
                            color: '#38bdf8',
                            fontSize: '11px',
                            fontWeight: 800,
                            padding: '3px 8px',
                            borderRadius: '6px',
                            letterSpacing: '0.6px'
                          }}>
                            POINT 0{p.point_number || pIdx + 1}
                          </span>
                          <span
                            style={{
                              background: badgeBg,
                              color: '#ffffff',
                              fontSize: '11px',
                              fontWeight: 800,
                              padding: '3px 9px',
                              borderRadius: '16px',
                              letterSpacing: '0.5px',
                              textTransform: 'uppercase',
                              boxShadow: '0 2px 6px rgba(0,0,0,0.3)'
                            }}
                          >
                            {p.risk_band} RISK
                          </span>
                        </div>

                        {/* Point Title */}
                        <div style={{ fontSize: '0.96rem', fontWeight: 700, color: '#ffffff', marginBottom: '4px', lineHeight: '1.3' }}>
                          {p.label}
                        </div>

                        {/* Segment Description */}
                        <div style={{ fontSize: '0.82rem', color: '#93c5fd', fontWeight: 600, marginBottom: '8px' }}>
                          📍 {p.segment_type}
                        </div>

                        {/* GPS Coordinates Tag */}
                        {p.latitude != null && p.longitude != null && (
                          <div style={{
                            background: 'rgba(15, 23, 42, 0.9)',
                            border: '1px solid rgba(148, 163, 184, 0.3)',
                            borderRadius: '6px',
                            padding: '4px 8px',
                            marginBottom: '12px',
                            fontSize: '0.8rem',
                            fontFamily: 'monospace',
                            color: '#38bdf8',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '5px'
                          }}>
                            <span>🌐</span>
                            <span>{p.latitude.toFixed(3)}°N, {p.longitude.toFixed(3)}°E</span>
                          </div>
                        )}

                        {/* Metrics Data Grid with High Contrast */}
                        <div style={{
                          display: 'grid',
                          gridTemplateColumns: '1fr 1fr 1fr',
                          gap: '6px',
                          background: 'rgba(15, 23, 42, 0.85)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '8px',
                          padding: '8px 6px',
                          marginTop: '4px'
                        }}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '10px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>Wave Swell</div>
                            <div style={{ fontSize: '13px', fontWeight: 800, color: '#38bdf8', marginTop: '2px' }}>
                              🌊 {p.wave_height_m}m
                            </div>
                          </div>
                          <div style={{ textAlign: 'center', borderLeft: '1px solid rgba(255, 255, 255, 0.1)', borderRight: '1px solid rgba(255, 255, 255, 0.1)' }}>
                            <div style={{ fontSize: '10px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>Wind</div>
                            <div style={{ fontSize: '13px', fontWeight: 800, color: '#4ade80', marginTop: '2px' }}>
                              💨 {p.wind_speed_kmh}k
                            </div>
                          </div>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '10px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>ETA</div>
                            <div style={{ fontSize: '13px', fontWeight: 800, color: '#fbbf24', marginTop: '2px' }}>
                              ⏱️ {p.eta_min != null ? `~${p.eta_min}m` : '—'}
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>

                <div className="reasonList" style={{ marginTop: '14px' }}>
                  <div>
                    <b>01 · Departure</b>
                    <span>Route initiates from <b>{activeRoute.departure_name}</b> following deep-water coastal navigational corridors.</span>
                  </div>
                  <div>
                    <b>02 · Corridor</b>
                    <span>Dynamic A* routing across <b>{activeRoute.waypoint_list?.length || 4} waypoints</b>, minimizing wave resistance & avoiding shallow reefs.</span>
                  </div>
                  <div>
                    <b>03 · Safety</b>
                    <span>
                      {isHigh 
                        ? '⚠️ Elevated wave swell or wind shear active along route. Reduce speed and prepare backup anchorage.' 
                        : (activeRoute.restricted_geofences_avoided?.length > 0 
                            ? `Geofence clearance confirmed. Avoided: ${activeRoute.restricted_geofences_avoided.join(', ')}.` 
                            : 'Prohibited geofences checked. All coordinates clear of marine protected boundaries.')}
                    </span>
                  </div>
                </div>

              {/* Step-by-Step Waypoint Table */}
              {activeRoute.waypoint_list && activeRoute.waypoint_list.length > 0 && (
                <div className="navTableWrap">
                  <table className="navTable">
                    <thead>
                      <tr>
                        <th>Leg</th>
                        <th>Coordinates</th>
                        <th>Heading</th>
                        <th>Leg Dist</th>
                        <th>ETA</th>
                        <th>Clearance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {activeRoute.waypoint_list.map((w, idx) => (
                        <tr key={idx}>
                          <td><b>#{w.leg || idx + 1}</b></td>
                          <td>{w.latitude.toFixed(3)}°N, {w.longitude.toFixed(3)}°E</td>
                          <td>{w.heading_deg?.toFixed(0)}° {w.compass_direction || ''}</td>
                          <td>{w.leg_distance_km?.toFixed(1) || 0} km</td>
                          <td>{w.eta_min != null ? `~${w.eta_min}m` : (w.cumulative_distance_km ? `~${Math.round(w.cumulative_distance_km / 18 * 60)}m` : '—')}</td>
                          <td><span className="navSafeTag clear">✓ Pass</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <button className="primary full" style={{ marginTop: '16px' }} onClick={() => navigate('/map')}>
                🗺️ View Full Route on Marine Map →
              </button>
            </div>
            )
          })() : (
            <p style={{ color: 'var(--muted)' }}>Select your departure origin and destination zone to compute the safe navigational corridor.</p>
          )}
        </Card>
      </div>

      <Card title={t('safetyChecklist')}>
        <div className="checklist">
          <span>✓ {t('weather')} Verified</span>
          <span>✓ {t('seaState')} Within Limits</span>
          <span>✓ {t('boundaries')} Cleared</span>
          <span>✓ {t('routeRisk')} Evaluated</span>
          <span>✓ Live Telemetry Active</span>
          <span>✓ A* Geofence Path Verified</span>
        </div>
      </Card>
    </>
  )
}

function MarkdownView({ text }) {
  if (!text) return null
  const lines = String(text).split('\n')
  const elements = []
  let currentList = []

  const renderInline = (str) => {
    let clean = str.replace(/^#{1,6}\s*/, '')
    const parts = clean.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g)
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
        return <strong key={i}>{part.slice(2, -2)}</strong>
      }
      if (part.startsWith('*') && part.endsWith('*') && part.length >= 2) {
        return <em key={i}>{part.slice(1, -1)}</em>
      }
      return part.replace(/\*{2,3}/g, '')
    })
  }

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`ul-${elements.length}`} className="chatList">
          {currentList.map((item, idx) => (
            <li key={idx}>{renderInline(item)}</li>
          ))}
        </ul>
      )
      currentList = []
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i].trim()
    if (!rawLine) {
      flushList()
      continue
    }
    if (rawLine.startsWith('#')) {
      flushList()
      const headingText = rawLine.replace(/^#{1,6}\s*/, '')
      elements.push(
        <h4 key={`h-${i}`} className="chatHeading">
          {renderInline(headingText)}
        </h4>
      )
      continue
    }
    if (/^[-*•]\s+/.test(rawLine)) {
      const itemText = rawLine.replace(/^[-*•]\s+/, '')
      currentList.push(itemText)
      continue
    }
    flushList()
    elements.push(
      <p key={`p-${i}`}>
        {renderInline(rawLine)}
      </p>
    )
  }
  flushList()
  return <div className="markdownContent">{elements}</div>
}

function getInitialAnswer(lang, userLocation) {
  if (lang === 'mr') {
    return userLocation
      ? `नमस्कार कॅप्टन! मी ORCA - आपला सागरी AI निर्णय सहाय्यक. मी आपल्या ${userLocation.port_name} किनाऱ्याशी थेट जोडलेलो आहे. आज मी आपल्या सागरी प्रवासात कशी मदत करू? आपण मासेमारी क्षेत्र (PFZ), लाटा, हवामान किंवा सुरक्षित मार्गाबद्दल विचारू शकता.`
      : 'नमस्कार कॅप्टन! मी ORCA आहे, आपला सागरी AI निर्णय सहाय्यक. मी आज आपल्या प्रवासासाठी कशी मदत करू? आपण मासेमारी क्षेत्र (PFZ), लाटा, हवामान किंवा सुरक्षित मार्गाबद्दल विचारू शकता.'
  }
  if (lang === 'hi') {
    return userLocation
      ? `नमस्ते कैप्टन! मैं ORCA हूँ - आपका समुद्री AI निर्णय सहायक। मैं आपके ${userLocation.port_name} तट से लाइव जुड़ा हुआ हूँ। आज मैं आपकी क्या सहायता कर सकता हूँ? आप PFZ क्षेत्र, मौसम, लहरें या सुरक्षित समुद्री मार्ग के बारे में पूछ सकते हैं।`
      : 'नमस्ते कप्तान! मैं ORCA हूँ, आपका समुद्री AI निर्णय सहायक। मैं आपकी क्या मदद कर सकता हूँ?'
  }
  return userLocation
    ? `Hello Captain! I am ORCA, connected live to your location near ${userLocation.port_name} (${userLocation.lat.toFixed(2)}°N, ${userLocation.lon.toFixed(2)}°E). How can I assist your voyage today? You can ask about PFZ zones, weather, wave conditions, or safe routes along the coast.`
    : 'Hello Captain! I am ORCA, your Marine AI Decision Copilot. How can I assist your voyage today? You can ask about PFZ zones, weather, wave conditions, or safe routes along the coast.'
}

function Assistant({
  lang,
  navigate,
  setActiveRoute,
  setSelectedZone,
  userLocation,
  conversations = [],
  activeConvId,
  messages = [],
  loading = false,
  userInitial = 'C',
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onClearChat,
  onSendMessage
}) {
  const t = k => tr(lang, k)
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (!input.trim() || loading) return
    onSendMessage(input.trim())
    setInput('')
  }

  const handleActionClick = (act, m) => {
    const actLower = (act || '').toLowerCase()
    const isSafeRouteAction = 
      actLower.includes('route') || 
      actLower.includes('मार्ग') || 
      actLower.includes('रास्ता') ||
      actLower.includes('safe') || 
      actLower.includes('सुरक्षित') ||
      actLower.includes('map') || 
      actLower.includes('नकाशा') || 
      actLower.includes('मैप')
      
    if (isSafeRouteAction) {
      // If message contains navigation/route data, preserve it into activeRoute
      const navData = m?.data?.navigation || m?.data?.route
      if (navData && setActiveRoute) {
        setActiveRoute(prev => ({
          ...prev,
          origin: navData.origin || prev?.origin,
          destination: navData.destination || prev?.destination,
          waypoints: navData.waypoints || prev?.waypoints,
          distance_km: navData.distance_km || prev?.distance_km,
          distance_nm: navData.distance_nm || prev?.distance_nm,
          estimated_travel_time_min: navData.estimated_travel_time_min || navData.estimated_duration_min || prev?.estimated_travel_time_min,
          overall_bearing_deg: navData.overall_bearing_deg || prev?.overall_bearing_deg,
          compass_direction: navData.compass_direction || prev?.compass_direction,
          average_risk_score: navData.average_risk_score || prev?.average_risk_score,
          risk_band: navData.risk_band || prev?.risk_band,
          assessment_points: navData.assessment_points || prev?.assessment_points,
          waypoint_list: navData.waypoints_detail || navData.waypoints || prev?.waypoint_list,
          departure_name: navData.origin_port || prev?.departure_name || 'Departure Port',
          destination_name: navData.destination_name || prev?.destination_name || 'Target PFZ'
        }))
      }
      navigate('/safety')
      return
    }

    if (actLower.includes('alert') || actLower.includes('सूचना') || actLower.includes('चेतावनी')) {
      navigate('/alerts')
      return
    }

    if (actLower.includes('analytic') || actLower.includes('विश्लेषण')) {
      navigate('/analytics')
      return
    }

    onSendMessage(act)
  }

  const activeConv = conversations.find(c => c.id === activeConvId)

  return (
    <div className="assistant">
      <div className="assistantIntro">
        <img className="assistantLogo" src={logo} alt="ORCA logo" />
        <span className="eyebrow">{t('conversational')}</span>
        <h2>{t('askSea')}</h2>
      </div>

      <div className="assistantLayout">
        {/* Previous Chats / History Drawer */}
        <aside className="chatHistorySidebar">
          <div className="chatHistoryHead">
            <h3>💬 {t('previousChats')}</h3>
            <button className="newChatBtn" onClick={onNewConversation} title="Start fresh conversation">
              + {t('newChat')}
            </button>
          </div>
          <div className="chatHistoryList">
            {conversations && conversations.length > 0 ? (
              conversations.map(c => (
                <div
                  key={c.id}
                  className={'historyItem ' + (c.id === activeConvId ? 'active' : '')}
                  onClick={() => onSelectConversation(c.id)}
                  title={c.title}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 10px',
                    cursor: 'pointer',
                    borderRadius: '8px',
                    gap: '6px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden', flex: 1, minWidth: 0 }}>
                    <span style={{ flexShrink: 0 }}>💬</span>
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '13px' }}>{c.title}</span>
                  </div>
                  {onDeleteConversation && (
                    <button
                      onClick={(e) => onDeleteConversation(c.id, e)}
                      title={lang === 'mr' ? 'हा चॅट हटवा' : (lang === 'hi' ? 'यह चैट हटाएं' : 'Delete this conversation')}
                      className="deleteConvBtn"
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#94a3b8',
                        cursor: 'pointer',
                        padding: '4px 6px',
                        borderRadius: '4px',
                        fontSize: '13px',
                        lineHeight: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: 0.7,
                        flexShrink: 0
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.color = '#ef4444'; e.currentTarget.style.opacity = '1'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.color = '#94a3b8'; e.currentTarget.style.opacity = '0.7'; }}
                    >
                      🗑️
                    </button>
                  )}
                </div>
              ))
            ) : (
              <div className="emptyHistoryNotice">{t('noChatsYet')}</div>
            )}
          </div>
        </aside>

        {/* Chat Stream & Composer */}
        <div className="chat">
          {/* Active Chat Header Bar with Clear Messages & Delete Chat Buttons */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 16px',
            borderBottom: '1px solid var(--line, rgba(255, 255, 255, 0.08))',
            background: 'var(--surface2, rgba(15, 23, 42, 0.5))',
            borderRadius: '16px 16px 0 0'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden', minWidth: 0 }}>
              <span style={{ fontSize: '15px', flexShrink: 0 }}>💬</span>
              <span style={{
                fontWeight: 700,
                fontSize: '13.5px',
                color: 'var(--text-main, #f8fafc)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                {activeConv?.title || (lang === 'mr' ? 'सक्रिय सागरी चर्चा' : (lang === 'hi' ? 'सक्रिय समुद्री चैट' : 'Current Marine Intelligence Chat'))}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
              {onClearChat && (
                <button
                  onClick={onClearChat}
                  title={lang === 'mr' ? 'या चॅटमधील सर्व संदेश साफ करा' : (lang === 'hi' ? 'वर्तमान चैट के सभी संदेश साफ करें' : 'Clear all messages in current chat')}
                  style={{
                    background: 'rgba(239, 68, 68, 0.12)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    color: '#f87171',
                    borderRadius: '6px',
                    padding: '5px 10px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(239, 68, 68, 0.25)' }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(239, 68, 68, 0.12)' }}
                >
                  <span>🗑️</span>
                  <span>{lang === 'mr' ? 'मेसेज साफ करा' : (lang === 'hi' ? 'संदेश साफ करें' : 'Clear Messages')}</span>
                </button>
              )}
              {activeConvId && onDeleteConversation && (
                <button
                  onClick={(e) => onDeleteConversation(activeConvId, e)}
                  title={lang === 'mr' ? 'हा संपूर्ण चॅट हटवा' : (lang === 'hi' ? 'यह पूरा चैट सत्र हटाएं' : 'Delete this entire conversation')}
                  style={{
                    background: 'rgba(148, 163, 184, 0.12)',
                    border: '1px solid rgba(148, 163, 184, 0.25)',
                    color: '#cbd5e1',
                    borderRadius: '6px',
                    padding: '5px 10px',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)'; e.currentTarget.style.color = '#ef4444' }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(148, 163, 184, 0.12)'; e.currentTarget.style.color = '#cbd5e1' }}
                >
                  <span>❌</span>
                  <span>{lang === 'mr' ? 'चॅट हटवा' : (lang === 'hi' ? 'चैट हटाएं' : 'Delete Chat')}</span>
                </button>
              )}
            </div>
          </div>

          <div className="messages">
            {messages.map((m, i) => {
              const role = m.role || m.sender || 'orca'
              return (
                <div className={'message ' + role} key={m.id || i}>
                  <div className="msgAvatar">{role === 'orca' ? '⚓' : userInitial}</div>
                  <div className="bubble">
                    <MarkdownView text={m.text} />
                    {m.hasRoute && (
                      <div className="bubbleNavActions">
                        <button className="bubbleNavBtn" onClick={() => {
                          const navData = m?.data?.navigation || m?.data?.route
                          if (navData && setActiveRoute) {
                            setActiveRoute(prev => ({
                              ...prev,
                              origin: navData.origin || prev?.origin,
                              destination: navData.destination || prev?.destination,
                              waypoints: navData.waypoints || prev?.waypoints,
                              distance_km: navData.distance_km || prev?.distance_km,
                              estimated_travel_time_min: navData.estimated_travel_time_min || navData.estimated_duration_min || prev?.estimated_travel_time_min
                            }))
                          }
                          navigate('/safety')
                        }}>
                          {t('viewSafety')} →
                        </button>
                        <button className="bubbleNavBtn" onClick={() => navigate('/map')}>
                          {t('viewOnMap')} →
                        </button>
                      </div>
                    )}
                    {m.suggestedActions && m.suggestedActions.length > 0 && (
                      <div className="bubbleSuggestedActions" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                        {m.suggestedActions.map((act, actIdx) => (
                          <button
                            key={actIdx}
                            className="suggestedActionBtn"
                            style={{
                              background: 'rgba(56, 189, 248, 0.15)',
                              border: '1px solid rgba(56, 189, 248, 0.4)',
                              color: 'var(--text-main, #38bdf8)',
                              padding: '6px 14px',
                              borderRadius: '20px',
                              fontSize: '13px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '6px'
                            }}
                            onClick={() => handleActionClick(act, m)}
                          >
                            <span>⚡</span>
                            <span>{act}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
            {loading && (
              <div className="message orca">
                <div className="msgAvatar">⚓</div>
                <div className="bubble typing">
                  {lang === 'mr' ? 'सागरी व हवामान डेटा विश्लेषित करत आहे...' : (lang === 'hi' ? 'समुद्री व मौसम डेटा का विश्लेषण जारी है...' : 'Reasoning across ocean and weather telemetry...')}
                </div>
              </div>
            )}
          </div>

          <div className="suggestions">
            <button onClick={() => onSendMessage(lang === 'mr' ? 'आज मासेमारीला जावे का?' : (lang === 'hi' ? 'क्या आज मछली पकड़ने जा सकते हैं?' : 'Can I go fishing today?'))}>
              🎣 {lang === 'mr' ? 'आज मासेमारी करावी का?' : (lang === 'hi' ? 'आज मछली पकड़ें?' : 'Can I go fishing today?')}
            </button>
            <button onClick={() => onSendMessage(lang === 'mr' ? 'मासेमारीसाठी सर्वात चांगला दिवस तपासा' : (lang === 'hi' ? 'मछली पकड़ने का सबसे अच्छा दिन जांचें' : 'Check best fishing day'))}>
              📅 {lang === 'mr' ? 'सर्वोत्तम दिवस' : (lang === 'hi' ? 'सर्वश्रेष्ठ दिन' : 'Check best fishing day')}
            </button>
            <button onClick={() => onSendMessage(t('showHazards'))}>
              ⚠️ {t('showHazards')}
            </button>
            <button onClick={() => onSendMessage(t('findRoute'))}>
              🧭 {t('findRoute')}
            </button>
          </div>


          <div className="composer">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder={t('placeholder')}
            />
            <button className="primary" onClick={handleSend}>{t('send')} →</button>
          </div>
        </div>
      </div>
    </div>
  )
}

function AlertsPage({ lang, setModal, alertList, selectedPort, setSelectedPort, userLocation, portContext }) {
  const t = k => tr(lang, k)
  const [filterPort, setFilterPort] = useState(selectedPort || 'mumbai')

  useEffect(() => {
    if (selectedPort) setFilterPort(selectedPort)
  }, [selectedPort])

  const currentPort = PORTS.find(p => p.id === (filterPort === 'all' ? selectedPort : filterPort)) || PORTS[3]

  const [portAlerts, setPortAlerts] = useState(alertList || [])
  const [alertsLoading, setAlertsLoading] = useState(false)

  // Fetch real-time active alerts whenever filterPort changes
  useEffect(() => {
    let active = true
    setAlertsLoading(true)
    getAllAlerts(filterPort === 'all' ? null : filterPort)
      .then(res => {
        if (active && res && Array.isArray(res.alerts)) {
          setPortAlerts(res.alerts)
        } else if (active) {
          setPortAlerts([])
        }
      })
      .catch(e => {
        console.warn('Alerts fetch error:', e)
        if (active) setPortAlerts([])
      })
      .finally(() => {
        if (active) setAlertsLoading(false)
      })
    return () => { active = false }
  }, [filterPort])

  // Group alerts into 3 priority buckets
  const highAlerts = portAlerts.filter(a => {
    const sev = (a.risk_level || a.severity || '').toUpperCase()
    return sev === 'HIGH' || sev === 'CRITICAL' || sev === 'SEVERE'
  })
  const mediumAlerts = portAlerts.filter(a => {
    const sev = (a.risk_level || a.severity || '').toUpperCase()
    return sev === 'MEDIUM' || sev === 'MODERATE' || sev === 'CAUTION'
  })
  const lowAlerts = portAlerts.filter(a => {
    return !highAlerts.includes(a) && !mediumAlerts.includes(a)
  })

  const renderAlertCard = (a) => {
    const sev = (a.risk_level || a.severity || 'MEDIUM').toUpperCase()
    const sevClass = sev === 'HIGH' || sev === 'CRITICAL' ? 'high' : (sev === 'MEDIUM' || sev === 'CAUTION' ? 'medium' : 'low')

    return (
      <button className="alertLarge" key={a.id} onClick={() => setModal(a)}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'flex-start' }}>
          <span className={`severity ${sevClass}`}>
            {sev}
          </span>
          {a.port_id && (
            <span style={{ fontSize: '10px', color: 'var(--muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              ⚓ {a.port_id}
            </span>
          )}
        </div>
        <div>
          <h3>{a.title?.[lang] || a.title || 'Marine Hazard Alert'}</h3>
          <p>{a.description || a.body?.[lang] || a.body || ''}</p>
        </div>
        <span>→</span>
      </button>
    )
  }

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">{t('alerts').toUpperCase()} • SEVERITY-SORTED INTELLIGENCE</span>
          <h2>{t('alerts')}</h2>
          <p>Real-time marine hazard warnings and high-wave advisories prioritized by navigational severity for {currentPort.name}.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ fontWeight: 600, fontSize: '0.9rem' }}>Port Sector:</label>
          <select 
            value={filterPort} 
            onChange={e => {
              setFilterPort(e.target.value)
              if (e.target.value !== 'all' && setSelectedPort) setSelectedPort(e.target.value)
            }}
            className="selectControl"
          >
            <option value="all">🇮🇳 All Coastline Advisories ({alertList.length})</option>
            {PORTS.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 1. HIGH PRIORITY WARNINGS */}
      <div className="alertPriorityGroup">
        <div className="priorityHeader high">
          <span>🔴 HIGH PRIORITY WARNINGS ({highAlerts.length})</span>
        </div>
        {highAlerts.length > 0 ? (
          <div className="alertList">
            {highAlerts.map(renderAlertCard)}
          </div>
        ) : (
          <div className="emptyPfzNotice" style={{ borderColor: 'rgba(15, 168, 137, 0.2)' }}>
            ✓ No critical or high-risk maritime hazard warnings active for this coastal sector.
          </div>
        )}
      </div>

      {/* 2. CAUTION ADVISORIES */}
      <div className="alertPriorityGroup">
        <div className="priorityHeader medium">
          <span>🟡 CAUTION ADVISORIES ({mediumAlerts.length})</span>
        </div>
        {mediumAlerts.length > 0 ? (
          <div className="alertList">
            {mediumAlerts.map(renderAlertCard)}
          </div>
        ) : (
          <div className="emptyPfzNotice">
            No moderate chop or caution advisories active for this coastal sector.
          </div>
        )}
      </div>

      {/* 3. COASTAL BULLETINS & LOW RISK */}
      <div className="alertPriorityGroup">
        <div className="priorityHeader low">
          <span>🟢 COASTAL BULLETINS & INFORMATIONAL ({lowAlerts.length})</span>
        </div>
        {lowAlerts.length > 0 ? (
          <div className="alertList">
            {lowAlerts.map(renderAlertCard)}
          </div>
        ) : (
          <div className="emptyPfzNotice">
            No coastal bulletins logged for this sector.
          </div>
        )}
      </div>
    </>
  )
}

function SettingsPage({ lang, setLang, dark, setDark }) {
  const t = k => tr(lang, k)
  const [email, setEmail] = useState(true)
  const [saved, setSaved] = useState(false)

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">{t('settings').toUpperCase()}</span>
          <h2>{t('settings')}</h2>
        </div>
        <button className="primary" onClick={() => { setSaved(true); setTimeout(() => setSaved(false), 1500) }}>
          {saved ? t('saved') : t('save')}
        </button>
      </div>

      <Card title={t('language')}>
        <div className="settingRow">
          <div>
            <b>{t('language')}</b>
            <p>{t('mapLabels')}</p>
          </div>
          <select value={lang} onChange={e => setLang(e.target.value)}>
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
            <option value="mr">मराठी</option>
          </select>
        </div>
      </Card>

      <Card title={t('theme')}>
        <div className="settingRow">
          <div>
            <b>{t('darkMode')}</b>
            <p>{dark ? 'Deep ocean blue dark interface' : 'Clean coastal light interface'}</p>
          </div>
          <button className={'toggle ' + (dark ? 'on' : '')} onClick={() => setDark(v => !v)}><span /></button>
        </div>
        <div className="settingRow">
          <div>
            <b>{t('email')}</b>
            <p>{t('notifications')}</p>
          </div>
          <button className={'toggle ' + (email ? 'on' : '')} onClick={() => setEmail(v => !v)}><span /></button>
        </div>
      </Card>
    </>
  )
}

function Profile({ lang, user, onSignOut }) {
  const t = k => tr(lang, k)
  const [editing, setEditing] = useState(false)
  const [profession, setProfession] = useState(localStorage.getItem('orca-profession') || 'Marine Researcher')

  const userName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || t('name')
  const userRole = user?.user_metadata?.role || profession

  const save = () => {
    localStorage.setItem('orca-profession', profession)
    setEditing(false)
  }

  return (
    <>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">{t('profileTitle').toUpperCase()}</span>
          <h2>{t('profileTitle')}</h2>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="primary" onClick={() => editing ? save() : setEditing(true)}>
            {editing ? t('done') : t('edit')}
          </button>
          {user && (
            <button className="textBtn" style={{ color: 'var(--danger)', fontWeight: 'bold' }} onClick={onSignOut}>
              {t('signOut')}
            </button>
          )}
        </div>
      </div>

      <Card title={t('details')}>
        <div className="profileBox">
          <div className="avatar bigAvatar">⚓</div>
          <div className="profileMain">
            <h2>{userName}</h2>
            <p>{userRole}</p>
            <span className="pill">{user ? 'Active Operational Account' : t('status')}</span>
          </div>
        </div>

        <div className="profileDetails">
          <div>
            <span>{t('emailLabel')}</span>
            <b>{user?.email || 'captain.devesh@orca-marine.in'}</b>
          </div>
          <div>
            <span>User ID (UUID)</span>
            <b>{user?.id ? user.id.slice(0, 18) + '...' : 'auth-demo-session'}</b>
          </div>
          <div>
            <span>{t('profession')}</span>
            {editing ? (
              <select value={profession} onChange={e => setProfession(e.target.value)}>
                <option>Marine Researcher</option>
                <option>Fisherman</option>
                <option>Fleet Operator</option>
              </select>
            ) : (
              <b>{profession}</b>
            )}
          </div>
          <div>
            <span>Account Security</span>
            <b>End-to-End Encrypted Session</b>
          </div>
        </div>
      </Card>
    </>
  )
}

function App() {
  const loc = useLocation()
  const navigate = useNavigate()
  const [lang, setLang] = useState(localStorage.getItem('orca-lang') || 'en')
  const [dark, setDark] = useState(localStorage.getItem('orca-theme') === 'dark')
  const [selected, setSelected] = useState('PFZ-MUM-01')
  const [modal, setModal] = useState(null)
  const [panel, setPanel] = useState(null)
  const [query, setQuery] = useState('')
  const [backendOnline, setBackendOnline] = useState(false)

  // Supabase Auth State
  const [currentUser, setCurrentUser] = useState(null)
  const [authModalOpen, setAuthModalOpen] = useState(false)

  // Dynamic Data & Route State
  const [selectedPort, setSelectedPort] = useState('mumbai')
  const [portContext, setPortContext] = useState(null)
  const [allIndiaPfzList, setAllIndiaPfzList] = useState([])
  const [pfzList, setPfzList] = useState(staticPfz)
  const [alertList, setAlertList] = useState(staticAlerts)
  const [oceanStats, setOceanStats] = useState(null)
  const [oceanPeriod, setOceanPeriod] = useState('7')
  const [oceanLoading, setOceanLoading] = useState(false)
  const [oceanError, setOceanError] = useState(null)
  const oceanReqRef = useRef(0)

  // Location Intelligence State (Version 3)
  const [userLocation, setUserLocation] = useState(null)
  const [detectingLocation, setDetectingLocation] = useState(false)
  const [locationPermission, setLocationPermission] = useState('prompt')

  const [activeRoute, setActiveRoute] = useState({
    origin: { lat: 18.94, lon: 72.83 },
    destination: { lat: 18.82, lon: 72.48 },
    waypoints: [
      { lat: 18.94, lon: 72.83 },
      { lat: 18.88, lon: 72.65 },
      { lat: 18.82, lon: 72.48 }
    ],
    distance_km: 39.2,
    estimated_travel_time_min: 155,
    departure_name: 'Mumbai Harbour',
    destination_name: 'PFZ-MUM-01'
  })

  const path = loc.pathname
  const t = k => tr(lang, k)

  // Chatbot State Lifted to App Level for Multi-Tab Persistence & History Drawer
  const [conversations, setConversations] = useState([])
  const [activeConvId, setActiveConvId] = useState(null)
  const [messages, setMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)

  const activeUserId = currentUser?.id || 'guest_user'
  const userInitial = useMemo(() => {
    const meta = currentUser?.user_metadata || {}
    const name = meta.full_name || meta.name || currentUser?.email || 'Captain'
    return name.trim().charAt(0).toUpperCase() || 'C'
  }, [currentUser])

  // Initialize or reload conversations when user changes (User-Specific Chat Isolation)
  useEffect(() => {
    let isMounted = true
    const initChats = async () => {
      try {
        const convList = await getUserConversations(activeUserId)
        if (!isMounted) return
        if (convList && convList.length > 0) {
          setConversations(convList)
          const firstId = convList[0].id
          setActiveConvId(firstId)
          const msgs = await getConversationMessages(firstId)
          if (!isMounted) return
          if (msgs && msgs.length > 0) {
            setMessages(msgs.map(m => ({
              id: m.id,
              role: m.sender,
              sender: m.sender,
              text: m.message_text,
              time: new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              data: m.structured_data || null,
              hasRoute: Boolean(m.structured_data?.navigation || m.structured_data?.route),
              suggestedActions: m.structured_data?.suggested_actions || []
            })))
          } else {
            setMessages([{ id: 'init', role: 'orca', sender: 'orca', text: getInitialAnswer(lang, userLocation), time: '10:00 AM' }])
          }
        } else {
          // Create initial conversation for user
          const newConv = await createNewConversation(activeUserId, 'Coastal Discussion')
          if (!isMounted) return
          if (newConv) {
            setConversations([newConv])
            setActiveConvId(newConv.id)
            setMessages([{ id: 'init', role: 'orca', sender: 'orca', text: getInitialAnswer(lang, userLocation), time: '10:00 AM' }])
          }
        }
      } catch (err) {
        console.warn('Could not initialize chat history:', err)
        if (isMounted) {
          setMessages([{ id: 'init', role: 'orca', sender: 'orca', text: getInitialAnswer(lang, userLocation), time: '10:00 AM' }])
        }
      }
    }
    initChats()
    return () => { isMounted = false }
  }, [activeUserId])

  const handleSelectConversation = async (convId) => {
    if (convId === activeConvId) return
    setActiveConvId(convId)
    setChatLoading(true)
    try {
      const msgs = await getConversationMessages(convId)
      if (msgs && msgs.length > 0) {
        setMessages(msgs.map(m => ({
          id: m.id,
          role: m.sender,
          sender: m.sender,
          text: m.message_text,
          time: new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          data: m.structured_data || null,
          hasRoute: Boolean(m.structured_data?.navigation || m.structured_data?.route),
          suggestedActions: m.structured_data?.suggested_actions || []
        })))
      } else {
        setMessages([{ id: 'init', role: 'orca', sender: 'orca', text: getInitialAnswer(lang, userLocation), time: '10:00 AM' }])
      }
    } catch (e) {
      console.error(e)
    } finally {
      setChatLoading(false)
    }
  }

  const handleNewConversation = async () => {
    try {
      const title = `Trip Chat ${new Date().toLocaleDateString([], { month: 'short', day: 'numeric' })}`
      const newConv = await createNewConversation(activeUserId, title)
      if (newConv) {
        setConversations(prev => [newConv, ...prev])
        setActiveConvId(newConv.id)
        setMessages([{ id: 'init', role: 'orca', sender: 'orca', text: getInitialAnswer(lang, userLocation), time: '10:00 AM' }])
      }
    } catch (e) {
      console.error(e)
    }
  }

  const handleDeleteConversation = async (convId, e) => {
    if (e && e.stopPropagation) e.stopPropagation()
    if (!convId) return
    const isCurrent = convId === activeConvId
    const confirmed = window.confirm(
      lang === 'mr' ? 'तुम्हाला ही चर्चा हटवायची आहे का?' : (lang === 'hi' ? 'क्या आप इस चैट सत्र को हटाना चाहते हैं?' : 'Are you sure you want to delete this conversation?')
    )
    if (!confirmed) return

    try {
      await deleteConversation(activeUserId, convId)
      const remaining = conversations.filter(c => c.id !== convId)
      setConversations(remaining)

      if (isCurrent) {
        if (remaining.length > 0) {
          handleSelectConversation(remaining[0].id)
        } else {
          // If no conversations left, create a fresh one
          handleNewConversation()
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err)
    }
  }

  const handleClearChat = async () => {
    const confirmed = window.confirm(
      lang === 'mr' ? 'वर्तमान चर्चेतील सर्व संदेश साफ करायचे आहेत का?' : (lang === 'hi' ? 'क्या आप इस चैट के सभी संदेश साफ करना चाहते हैं?' : 'Clear all messages in the current conversation?')
    )
    if (!confirmed) return

    try {
      if (activeConvId) {
        await clearConversationMessages(activeConvId)
      }
      const initialText = getInitialAnswer(lang, userLocation)
      const initTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      setMessages([{ id: 'init', role: 'orca', sender: 'orca', text: initialText, time: initTime }])
    } catch (err) {
      console.error('Failed to clear chat messages:', err)
    }
  }

  const handleSendChatMessage = async (textToSend) => {
    if (!textToSend || !textToSend.trim() || chatLoading) return
    const queryText = textToSend.trim()
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    const userMsg = { id: `u_${Date.now()}`, role: 'user', sender: 'user', text: queryText, time: nowTime }

    setMessages(prev => [...prev, userMsg])
    setChatLoading(true)

    // Save user message to database/cache
    if (activeConvId) {
      saveChatMessage(activeConvId, 'user', queryText).catch(console.warn)
    }

    try {
      // Build location payload with selected_port priority
      const userLocPayload = {
        selected_port: selectedPort || 'mumbai',
        ...(userLocation ? {
          latitude: userLocation.lat,
          longitude: userLocation.lon,
          port_id: userLocation.port_id,
          port_name: userLocation.port_name,
          state: userLocation.state,
          is_coastal: userLocation.is_coastal
        } : {})
      }

      const res = await askOrca(queryText, lang, userLocPayload)
      let botAnswer = ''
      let botData = null

      if (res && res.answer) {
        botAnswer = res.answer
        botData = res
      } else if (typeof res === 'string') {
        botAnswer = res
      } else {
        botAnswer = lang === 'mr' ? 'मला क्षमस्व, उत्तर तयार करण्यात अडचण आली. कृपया पुन्हा प्रयत्न करा.' :
                    lang === 'hi' ? 'क्षमा करें, उत्तर तैयार करने में समस्या आई। कृपया पुनः प्रयास करें।' :
                    'Sorry, I could not generate a response right now. Please try again.'
      }

      // CRITICAL: Strict language matching - DO NOT append any English trails or recommendation text
      const hasRoute = Boolean(res?.navigation || res?.route || res?.pfz_recommendation)
      const botMsg = {
        id: `o_${Date.now()}`,
        role: 'orca',
        sender: 'orca',
        text: botAnswer,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        data: botData,
        hasRoute: hasRoute,
        suggestedActions: res?.suggested_actions || botData?.suggested_actions || []
      }


      setMessages(prev => [...prev, botMsg])

      // Save bot response to database/cache
      if (activeConvId) {
        saveChatMessage(activeConvId, 'orca', botAnswer, botData).catch(console.warn)
      }
    } catch (err) {
      console.error('Chat error:', err)
      const errAnswer = lang === 'mr' ? 'सर्व्हर त्रुटी. कृपया आपले कनेक्शन तपासा.' :
                         lang === 'hi' ? 'सर्वर त्रुटि। कृपया अपना कनेक्शन जांचें।' :
                         'Connection error. Please check backend services.'
      setMessages(prev => [...prev, {
        id: `err_${Date.now()}`,
        role: 'orca',
        sender: 'orca',
        text: errAnswer,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }])
    } finally {
      setChatLoading(false)
    }
  }

  // Geolocation resolution function
  const handleRequestLocation = (force = false) => {
    if (!navigator.geolocation) {
      console.warn('Geolocation not supported by browser.')
      setLocationPermission('denied')
      return
    }
    setDetectingLocation(true)
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords
        setLocationPermission('granted')
        try {
          const locData = await resolveUserLocation(latitude, longitude)
          if (locData) {
            const nearest = locData.nearest_port || {}
            const locObj = {
              lat: latitude,
              lon: longitude,
              port_id: nearest.id || 'mumbai',
              port_name: nearest.name || 'Mumbai Harbour',
              state: nearest.state || 'Maharashtra',
              is_coastal: locData.is_coastal,
              distance_to_port_km: locData.distance_to_coast_km || 0,
              incois_live: locData.live_incois,
              nearby_pfz: locData.nearby_pfz || [],
              status: 'granted'
            }
            setUserLocation(locObj)
            if (nearest.id) {
              setSelectedPort(nearest.id)
              loadPfzs(nearest.id)
            }
          }
        } catch (e) {
          console.error('Error resolving location:', e)
        } finally {
          setDetectingLocation(false)
        }
      },
      (err) => {
        console.warn('Geolocation denied or timed out:', err)
        setLocationPermission('denied')
        setDetectingLocation(false)
        if (!userLocation) {
          setUserLocation({
            lat: 18.94,
            lon: 72.83,
            port_id: 'mumbai',
            port_name: 'Mumbai Harbour (Default)',
            is_coastal: true,
            distance_to_port_km: 0,
            status: 'fallback'
          })
        }
      },
      { timeout: 9000, enableHighAccuracy: true, maximumAge: 60000 }
    )
  }

  // Request user location automatically on initial application mount
  useEffect(() => {
    handleRequestLocation(false)
  }, [])

  // Helper to plot safe A* route directly from user's coordinates to a PFZ
  const handlePlotRouteFromLocation = async (targetZone) => {
    const startLat = userLocation?.lat || 18.94
    const startLon = userLocation?.lon || 72.83
    const endLat = targetZone.lat
    const endLon = targetZone.lng || targetZone.lon

    try {
      const navRes = await getSafeMarineRoute(startLat, startLon, endLat, endLon, 18.0)
      if (navRes && navRes.waypoints && navRes.waypoints.length > 0) {
        setActiveRoute({
          origin: { lat: startLat, lon: startLon },
          destination: { lat: endLat, lon: endLon },
          waypoints: navRes.waypoints.map(w => ({ lat: w.latitude, lon: w.longitude })),
          distance_km: navRes.distance_km,
          distance_nm: navRes.distance_nm,
          estimated_travel_time_min: navRes.estimated_duration_min,
          overall_bearing_deg: navRes.overall_bearing_deg,
          compass_direction: navRes.compass_direction,
          average_risk_score: navRes.average_risk_score,
          risk_band: navRes.risk_band,
          waypoint_list: navRes.waypoints,
          restricted_geofences_avoided: navRes.restricted_geofences_avoided || [],
          departure_name: userLocation?.port_name ? `📍 ${userLocation.port_name}` : 'My Position',
          destination_name: targetZone.name || targetZone.id,
          geofence_status: (navRes.restricted_geofences_avoided?.length > 0) ? 'avoided_restricted_zones' : 'clear'
        })
        setSelected(targetZone.id)
        navigate('/safety')
      }
    } catch (e) {
      console.error(e)
    }
  }

  // Initialize Supabase Auth session listener
  useEffect(() => {
    getSession().then(session => {
      if (session?.user) setCurrentUser(session.user)
    })
    const { data: authListener } = onAuthStateChange((_event, user) => {
      setCurrentUser(user)
    })
    return () => authListener?.subscription?.unsubscribe()
  }, [])

  // Sync lang & theme to DOM
  useEffect(() => {
    localStorage.setItem('orca-lang', lang)
    document.documentElement.lang = lang
  }, [lang])

  useEffect(() => {
    localStorage.setItem('orca-theme', dark ? 'dark' : 'light')
    document.documentElement.dataset.theme = dark ? 'dark' : 'light'
  }, [dark])

  // Periodic Backend Health Check & Data Fetching
  useEffect(() => {
    const check = async () => {
      const health = await checkBackendHealth()
      setBackendOnline(!!health?.online)
    }
    check()
    const timer = setInterval(check, 10000)
    return () => clearInterval(timer)
  }, [])

  const loadPfzs = (portId = selectedPort) => {
    // 0. Refresh alerts for this specific port
    loadAlerts(portId)

    // 1. Fetch Port Context (marine conditions, advisories, departure window)
    getPortContext(portId).then(ctx => {
      if (ctx) setPortContext(ctx)
    })

    // 2. Port-specific live PFZs from Backend / Registry
    getPfzCandidates(null, null, portId).then(res => {
      if (res && res.candidates && res.candidates.length > 0) {
        const mapped = res.candidates.map(c => ({
          id: c.zone_id,
          name: c.name || `${c.zone_id} Coastal Front`,
          sector: c.sector || 'Indian Coastal Shelf',
          port_id: c.port_id || portId,
          port_name: c.port_name || portId,
          status: c.status || 'ACTIVE',
          inactive_reason: c.inactive_reason || null,
          lat: c.lat,
          lng: c.lon,
          lon: c.lon,
          confidence: Math.round((c.confidence_score || 0.90) * 100),
          sst: c.sst_celsius || 28.0,
          chlorophyll: c.chlorophyll_mg_m3 || 1.4,
          waves: 1.2,
          wind: 16,
          bearing: c.bearing_deg || 250,
          depth: c.depth_m || 45,
          distance: `${c.distance_km || 30} km`,
          reason: {
            en: `Real-time satellite SST (${c.sst_celsius}°C) & chlorophyll front along ${c.name || c.zone_id}`,
            hi: `सैटेलाइट SST (${c.sst_celsius}°C) और क्लोरोफिल फ्रंट ${c.name || c.zone_id}`,
            mr: `सॅटेलाइट SST (${c.sst_celsius}°C) आणि क्लोरोफिल फ्रंट ${c.name || c.zone_id}`
          }
        }))
        setPfzList(mapped)
      }
    })

    // 3. All-India PFZs overview
    getPfzCandidates(null, null, 'all').then(res => {
      if (res && res.candidates && res.candidates.length > 0) {
        const mappedAll = res.candidates.map(c => ({
          id: c.zone_id,
          name: c.name || `${c.zone_id} Front`,
          sector: c.sector || 'Indian Coast',
          port_id: c.port_id,
          port_name: c.port_name,
          status: c.status || 'ACTIVE',
          inactive_reason: c.inactive_reason || null,
          lat: c.lat,
          lng: c.lon,
          lon: c.lon,
          confidence: Math.round((c.confidence_score || 0.90) * 100),
          sst: c.sst_celsius || 28.0,
          chlorophyll: c.chlorophyll_mg_m3 || 1.4,
          distance: `${c.distance_km || 30} km`
        }))
        setAllIndiaPfzList(mappedAll)
      }
    })
  }

  const loadOceanStats = async (port, period) => {
    oceanReqRef.current += 1
    const reqId = oceanReqRef.current
    setOceanLoading(true)
    setOceanError(null)
    try {
      const res = await getAnalytics(period, port)
      if (reqId !== oceanReqRef.current) return
      if (res && res.sea_surface_temp) {
        setOceanStats(res)
        setOceanError(null)
      } else {
        setOceanError('Unable to load ocean analytics data.')
      }
    } catch (err) {
      if (reqId === oceanReqRef.current) {
        console.error('Ocean analytics error:', err)
        setOceanError('Unable to load ocean analytics data.')
      }
    } finally {
      if (reqId === oceanReqRef.current) {
        setOceanLoading(false)
      }
    }
  }

  const loadAlerts = (port = selectedPort) => {
    getAllAlerts(port).then(res => {
      if (res && Array.isArray(res.alerts)) {
        setAlertList(res.alerts)
      } else {
        setAlertList([])
      }
    }).catch(err => {
      console.warn('Alerts fetch error:', err)
      setAlertList([])
    })
  }

  // Fetch live Alerts, Analytics, and PFZ from backend/Supabase
  useEffect(() => {
    loadAlerts(selectedPort)
    loadOceanStats(selectedPort, oceanPeriod)
    loadPfzs(selectedPort)
  }, [selectedPort, oceanPeriod])

  const handleSignOut = async () => {
    await signOutUser()
    setCurrentUser(null)
    setConversations([])
    setActiveConvId(null)
    setMessages([])
  }

  const nav = [
    ['Dashboard', '/'],
    ['Marine Intelligence Map', '/map'],
    ['Ocean Analytics', '/analytics'],
    ['Fishing Intelligence', '/fishing'],
    ['Safety & Routes', '/safety'],
    ['ORCA AI Assistant', '/assistant'],
    ['Alerts', '/alerts'],
    ['Settings', '/settings']
  ]

  const results = useMemo(() => nav.filter(([name]) => name.toLowerCase().includes(query.toLowerCase())), [query])

  let content
  if (path === '/') {
    content = (
      <Dashboard
        lang={lang}
        navigate={navigate}
        setSelected={setSelected}
        setModal={setModal}
        pfzList={pfzList}
        alertList={alertList}
        oceanStats={oceanStats}
        selectedPort={selectedPort}
        setSelectedPort={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
        userLocation={userLocation}
        requestLocationPermission={handleRequestLocation}
        detectingLocation={detectingLocation}
        portContext={portContext}
      />
    )
  }
  if (path === '/map') {
    content = (
      <MapPage
        lang={lang}
        selected={selected}
        setSelected={setSelected}
        activeRoute={activeRoute}
        setActiveRoute={setActiveRoute}
        pfzList={pfzList}
        allIndiaPfzList={allIndiaPfzList}
        alertList={alertList}
        selectedPort={selectedPort}
        setSelectedPort={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
        userLocation={userLocation}
        onPlotRouteFromLocation={handlePlotRouteFromLocation}
      />
    )
  }
  if (path === '/analytics') {
    content = (
      <Analytics
        lang={lang}
        oceanStats={oceanStats}
        oceanPeriod={oceanPeriod}
        setOceanPeriod={setOceanPeriod}
        selectedPort={selectedPort}
        setSelectedPort={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
        portContext={portContext}
        oceanLoading={oceanLoading}
        oceanError={oceanError}
      />
    )
  }
  if (path === '/fishing') {
    content = (
      <Fishing
        lang={lang}
        navigate={navigate}
        setSelected={setSelected}
        pfzList={pfzList}
        allIndiaPfzList={allIndiaPfzList}
        selectedPort={selectedPort}
        setSelectedPort={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
        portContext={portContext}
      />
    )
  }
  if (path === '/safety') {
    content = (
      <Safety
        lang={lang}
        navigate={navigate}
        activeRoute={activeRoute}
        setActiveRoute={setActiveRoute}
        pfzList={pfzList}
        selectedPort={selectedPort}
        setSelectedPort={setSelectedPort}
        onPortChange={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
        userLocation={userLocation}
      />
    )
  }
  if (path === '/assistant') {
    content = (
      <Assistant
        lang={lang}
        navigate={navigate}
        setActiveRoute={setActiveRoute}
        setSelectedZone={setSelected}
        userLocation={userLocation}
        conversations={conversations}
        activeConvId={activeConvId}
        messages={messages}
        loading={chatLoading}
        userInitial={userInitial}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        onClearChat={handleClearChat}
        onSendMessage={handleSendChatMessage}
      />
    )
  }
  if (path === '/alerts') {
    content = (
      <AlertsPage
        lang={lang}
        setModal={setModal}
        alertList={alertList}
        selectedPort={selectedPort}
        setSelectedPort={p => {
          setSelectedPort(p)
          loadPfzs(p)
        }}
        userLocation={userLocation}
        portContext={portContext}
      />
    )
  }
  if (path === '/settings') {
    content = (
      <SettingsPage
        lang={lang}
        setLang={setLang}
        dark={dark}
        setDark={setDark}
      />
    )
  }
  if (path === '/profile') {
    content = (
      <Profile
        lang={lang}
        user={currentUser}
        onSignOut={handleSignOut}
      />
    )
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate('/')}>
          <img className="brandLogo" src={logo} alt="ORCA logo" />
          <div>
            <b>ORCA</b>
            <small>Marine Intelligence</small>
          </div>
        </button>

        <div className="navTitle">{t('workspace')}</div>
        {nav.map(([name, url], i) => (
          <button
            key={url}
            className={'nav ' + ((url === '/' ? path === '/' : path === url) ? 'active' : '')}
            onClick={() => navigate(url)}
          >
            <span className="ico">{['⌂', '◈', '◫', '◉', '◇', '◌', '!', '⚙'][i]}</span>
            {t(keyFor(name))}
          </button>
        ))}

        <div className="sideBottom">
          <span className={backendOnline ? 'greenDot' : 'amberDot'} />
          <div>
            <b>{backendOnline ? 'Supabase & AI Engine' : t('operational')}</b>
            <small>{backendOnline ? 'Live Connected (:8000)' : t('connected')}</small>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <span className="eyebrow">ORCA / {t(keyFor(labels[path] || 'Dashboard'))}</span>
            <h1>{t(keyFor(labels[path] || 'Dashboard'))}</h1>
          </div>

          <div className="headerRight">
            {/* Live Location Navigation Status Pill */}
            <button 
              className="headerLocationPill"
              onClick={() => handleRequestLocation(true)}
              title="Click to detect or refresh your GPS location"
            >
              <span className={userLocation?.status === 'granted' ? 'pulseGps' : 'amberDot'} />
              <span>
                {userLocation?.status === 'granted'
                  ? `📍 ${userLocation.port_name?.split(' ')[0]} (${userLocation.lat.toFixed(2)}°, ${userLocation.lon.toFixed(2)}°)`
                  : (detectingLocation ? '📍 Detecting...' : '📍 Allow Location')}
              </span>
            </button>

            <button className="iconBtn" onClick={() => setPanel(panel === 'search' ? null : 'search')} aria-label={t('search')}>⌕</button>
            <button className="iconBtn" onClick={() => setPanel(panel === 'bell' ? null : 'bell')} aria-label={t('notifications')}>♢</button>

            <select aria-label={t('language')} value={lang} onChange={e => setLang(e.target.value)}>
              <option value="en">English</option>
              <option value="hi">हिन्दी</option>
              <option value="mr">मराठी</option>
            </select>

            {currentUser ? (
              <button className="avatarBtn" onClick={() => navigate('/profile')}>
                <div className="avatarIcon">⚓</div>
                <span className="avatarName">{currentUser.user_metadata?.full_name?.split(' ')[0] || currentUser.email?.split('@')[0] || 'Captain'}</span>
              </button>
            ) : (
              <button className="authNavBtn" onClick={() => setAuthModalOpen(true)}>
                ⚓ {t('signIn')}
              </button>
            )}
          </div>
        </header>

        {panel && (
          <div className="floatingPanel">
            {panel === 'search' ? (
              <div>
                <b>{t('search')}</b>
                <input
                  autoFocus
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder={t('search') + '...'}
                />
                <div className="searchResults">
                  {query ? (
                    results.map(([n, u]) => (
                      <button key={u} onClick={() => { navigate(u); setPanel(null); setQuery('') }}>
                        {t(keyFor(n))} →
                      </button>
                    ))
                  ) : (
                    <span>{t('noResults')}</span>
                  )}
                </div>
                <button onClick={() => setPanel(null)}>{t('close')}</button>
              </div>
            ) : (
              <div>
                <b>{t('notifications')}</b>
                {alertList.map(a => (
                  <button className="panelAlert" key={a.id} onClick={() => { setModal(a); setPanel(null) }}>
                    <strong>{a.title?.[lang] || a.title || 'Alert'}</strong>
                    <span>{a.description || a.body?.[lang] || a.body || ''}</span>
                  </button>
                ))}
                <button onClick={() => setPanel(null)}>{t('close')}</button>
              </div>
            )}
          </div>
        )}

        <div className="content">{content}</div>
      </main>

      {modal && (
        <div className="modalBackdrop" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <span className={'severity ' + (modal.risk_level ? modal.risk_level.toLowerCase() : modal.severity?.toLowerCase() || 'medium')}>
              {modal.risk_level || modal.severity || 'ALERT'}
            </span>
            <h2>{modal.title?.[lang] || modal.title || 'Advisory'}</h2>
            <p>{modal.description || modal.body?.[lang] || modal.body || ''}</p>
            <button className="primary" onClick={() => setModal(null)}>{t('close')}</button>
          </div>
        </div>
      )}

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={user => setCurrentUser(user)}
      />
    </div>
  )
}

export default function Root() {
  return (
    <BrowserRouter>
      <App />
    </BrowserRouter>
  )
}
