import { useEffect, useRef, useState } from "react";

import "./App.css";



const STORAGE = {

  user: "voiceshield_user",

  trusted: "voiceshield_trusted_voices",

  history: "voiceshield_history",

  alerts: "voiceshield_alerts",

  settings: "voiceshield_settings",

};



function App() {

  const [user, setUser] = useState(() => {

    const saved = localStorage.getItem(STORAGE.user);

    return saved

      ? JSON.parse(saved)

      : {

          name: "Admin",

          email: "admin@voiceshield.ai",

          password: "admin123",

          profileImage: "",

        };

  });



  const [authenticated, setAuthenticated] = useState(

    () => localStorage.getItem("voiceshield_logged_in") === "true"

  );



  const [page, setPage] = useState(

    authenticated ? "dashboard" : "login"

  );



  const [trustedVoices, setTrustedVoices] = useState(() => {

    const saved = localStorage.getItem(STORAGE.trusted);

    return saved ? JSON.parse(saved) : [];

  });



  const [history, setHistory] = useState(() => {

    const saved = localStorage.getItem(STORAGE.history);

    return saved ? JSON.parse(saved) : [];

  });



  const [alerts, setAlerts] = useState(() => {

    const saved = localStorage.getItem(STORAGE.alerts);

    return saved ? JSON.parse(saved) : [];

  });



  const [settings, setSettings] = useState(() => {

    const saved = localStorage.getItem(STORAGE.settings);



    return saved

      ? JSON.parse(saved)

      : {

          notifications: true,

          darkMode: false,

          autoDeleteAudio: false,

          saveHistory: true,

        };

  });



  const [selectedAnalysis, setSelectedAnalysis] = useState(null);



  useEffect(() => {

    localStorage.setItem(STORAGE.user, JSON.stringify(user));

  }, [user]);



  useEffect(() => {

    localStorage.setItem(

      STORAGE.trusted,

      JSON.stringify(trustedVoices)

    );

  }, [trustedVoices]);



  useEffect(() => {

    localStorage.setItem(

      STORAGE.history,

      JSON.stringify(history)

    );

  }, [history]);



  useEffect(() => {

    localStorage.setItem(

      STORAGE.alerts,

      JSON.stringify(alerts)

    );

  }, [alerts]);



  useEffect(() => {

    localStorage.setItem(

      STORAGE.settings,

      JSON.stringify(settings)

    );

  }, [settings]);



  // -----------------------------

  // LOGIN

  // -----------------------------



  const login = (email, password) => {

    if (

      email === user.email &&

      password === user.password

    ) {

      localStorage.setItem(

        "voiceshield_logged_in",

        "true"

      );



      setAuthenticated(true);

      setPage("dashboard");



      return true;

    }



    return false;

  };



  const signup = (name, email, password) => {

    const newUser = {

      name,

      email,

      password,

      profileImage: "",

    };



    setUser(newUser);



    localStorage.setItem(

      STORAGE.user,

      JSON.stringify(newUser)

    );



    localStorage.setItem(

      "voiceshield_logged_in",

      "true"

    );



    setAuthenticated(true);

    setPage("dashboard");

  };



  const logout = () => {

    localStorage.removeItem(

      "voiceshield_logged_in"

    );



    setAuthenticated(false);

    setPage("login");

  };



  // -----------------------------

  // ADD TRUSTED VOICE

  // -----------------------------



  const addTrustedVoice = (voice) => {

    const newVoice = {

      id: Date.now(),

      name: voice.name,

      relation: voice.relation,

      fileName: voice.fileName,

      audioUrl: voice.audioUrl,

      profileImage: voice.profileImage || "",

      dateAdded: new Date().toLocaleDateString(),

      embeddingStatus: "Pending",

      verificationCount: 0,

    };



    setTrustedVoices((prev) => [

      ...prev,

      newVoice,

    ]);

  };



  const updateTrustedVoice = (updatedVoice) => {

    setTrustedVoices((prev) =>

      prev.map((voice) =>

        voice.id === updatedVoice.id

          ? updatedVoice

          : voice

      )

    );

  };



  const deleteTrustedVoice = (id) => {

    if (

      !window.confirm(

        "Remove this trusted voice?"

      )

    ) {

      return;

    }



    setTrustedVoices((prev) =>

      prev.filter((voice) => voice.id !== id)

    );

  };



  // -----------------------------

  // ANALYSIS

  // -----------------------------



  const addAnalysis = (result) => {

    const analysis = {

      ...result,

      id: Date.now(),

      date: new Date().toLocaleString(),

    };



    setHistory((prev) => [

      analysis,

      ...prev,

    ]);



    if (result.riskLevel === "HIGH") {

      const newAlert = {

        id: Date.now(),

        type: "HIGH",

        title: "High Risk Voice Detected",

        message:

          "The analyzed audio requires additional verification.",

        date: new Date().toLocaleString(),

      };



      setAlerts((prev) => [

        newAlert,

        ...prev,

      ]);

    }



    return analysis;

  };



  // -----------------------------

  // PROFILE

  // -----------------------------



  const updateProfile = (data) => {

    const updatedUser = {

      ...user,

      ...data,

    };



    setUser(updatedUser);



    localStorage.setItem(

      STORAGE.user,

      JSON.stringify(updatedUser)

    );

  };



  // -----------------------------

  // PAGE

  // -----------------------------



  if (!authenticated) {

    if (page === "signup") {

      return (

        <SignupPage

          onSignup={signup}

          onLogin={() => setPage("login")}

        />

      );

    }



    return (

      <LoginPage

        onLogin={login}

        onSignup={() => setPage("signup")}

      />

    );

  }



  return (

    <div

      className={

        settings.darkMode

          ? "app dark-mode"

          : "app"

      }

    >

      <Sidebar

        page={page}

        setPage={setPage}

        logout={logout}

        user={user}

      />



      <main className="main-content">



        <Header

          page={page}

          user={user}

          alerts={alerts}

          setPage={setPage}

        />



        <div className="page-content">



          {page === "dashboard" && (

            <Dashboard

              user={user}

              trustedVoices={trustedVoices}

              history={history}

              alerts={alerts}

              setPage={setPage}

            />

          )}



          {page === "analysis" && (

            <VoiceAnalysis

              trustedVoices={trustedVoices}

              addAnalysis={addAnalysis}

            />

          )}



          {page === "trusted" && (

            <TrustedVoices

              trustedVoices={trustedVoices}

              addTrustedVoice={addTrustedVoice}

              updateTrustedVoice={updateTrustedVoice}

              deleteTrustedVoice={deleteTrustedVoice}

            />

          )}



          {page === "history" && (

            <AnalysisHistory

              history={history}

              setSelectedAnalysis={

                setSelectedAnalysis

              }

              setPage={setPage}

            />

          )}



          {page === "details" && (

            <AnalysisDetails

              analysis={selectedAnalysis}

              setPage={setPage}

            />

          )}



          {page === "profile" && (

            <ProfilePage

              user={user}

              updateProfile={updateProfile}

            />

          )}



          {page === "settings" && (

            <SettingsPage

              settings={settings}

              setSettings={setSettings}

              logout={logout}

              setHistory={setHistory}

            />

          )}



          {page === "alerts" && (

            <AlertsPage

              alerts={alerts}

              setAlerts={setAlerts}

            />

          )}



        </div>

      </main>

    </div>

  );

}





// =====================================================

// LOGIN

// =====================================================



function LoginPage({

  onLogin,

  onSignup,

}) {

  const [email, setEmail] = useState("");

  const [password, setPassword] =

    useState("");



  const [error, setError] = useState("");



  const submit = (e) => {

    e.preventDefault();



    const success = onLogin(

      email,

      password

    );



    if (!success) {

      setError(

        "Invalid email or password."

      );

    }

  };



  return (

    <div className="auth-page">



      <div className="auth-brand">

        <div className="auth-logo">

          VS

        </div>



        <h1>VoiceShield AI</h1>



        <p>

          AI-Powered Voice Security

        </p>

      </div>



      <div className="auth-card">



        <h2>

          Welcome Back

        </h2>



        <p className="auth-subtitle">

          Sign in to your security dashboard

        </p>



        <form onSubmit={submit}>



          <label>Email Address</label>



          <input

            type="email"

            placeholder="you@example.com"

            value={email}

            onChange={(e) =>

              setEmail(e.target.value)

            }

            required

          />



          <label>Password</label>



          <input

            type="password"

            placeholder="Enter your password"

            value={password}

            onChange={(e) =>

              setPassword(e.target.value)

            }

            required

          />



          {error && (

            <div className="auth-error">

              {error}

            </div>

          )}



          <div className="auth-options">

            <label className="checkbox-label">

              <input type="checkbox" />

              Remember me

            </label>



            <button

              type="button"

              className="link-btn"

            >

              Forgot password?

            </button>

          </div>



          <button className="auth-btn">

            Sign In

          </button>



        </form>



        <div className="auth-divider">

          OR

        </div>



        <p className="signup-text">

          Don't have an account?



          <button

            className="link-btn"

            onClick={onSignup}

          >

            Create Account

          </button>

        </p>



      </div>



      <p className="auth-footer">

        🔒 Secure AI-powered voice protection

      </p>



    </div>

  );

}





// =====================================================

// SIGN UP

// =====================================================



function SignupPage({

  onSignup,

  onLogin,

}) {

  const [name, setName] =

    useState("");



  const [email, setEmail] =

    useState("");



  const [password, setPassword] =

    useState("");



  const submit = (e) => {

    e.preventDefault();



    onSignup(

      name,

      email,

      password

    );

  };



  return (

    <div className="auth-page">



      <div className="auth-brand">

        <div className="auth-logo">

          VS

        </div>



        <h1>VoiceShield AI</h1>



        <p>

          AI-Powered Voice Security

        </p>

      </div>



      <div className="auth-card">



        <h2>

          Create Account

        </h2>



        <p className="auth-subtitle">

          Set up your VoiceShield account

        </p>



        <form onSubmit={submit}>



          <label>Full Name</label>



          <input

            type="text"

            placeholder="Your name"

            value={name}

            onChange={(e) =>

              setName(e.target.value)

            }

            required

          />



          <label>Email Address</label>



          <input

            type="email"

            placeholder="you@example.com"

            value={email}

            onChange={(e) =>

              setEmail(e.target.value)

            }

            required

          />



          <label>Password</label>



          <input

            type="password"

            placeholder="Create password"

            value={password}

            onChange={(e) =>

              setPassword(e.target.value)

            }

            required

          />



          <button className="auth-btn">

            Create Account

          </button>



        </form>



        <p className="signup-text">

          Already have an account?



          <button

            className="link-btn"

            onClick={onLogin}

          >

            Sign In

          </button>

        </p>



      </div>



    </div>

  );

}





// =====================================================

// SIDEBAR

// =====================================================



function Sidebar({

  page,

  setPage,

  logout,

  user,

}) {

  const mainItems = [

    ["dashboard", "▦", "Dashboard"],

    ["analysis", "◉", "Voice Analysis"],

    ["trusted", "♙", "Trusted Voices"],

    ["history", "◷", "Analysis History"],

  ];



  return (

    <aside className="sidebar">



      <div className="logo-area">



        <div className="logo-icon">

          VS

        </div>



        <div>

          <h2>VoiceShield</h2>

          <span>AI Security</span>

        </div>



      </div>



      <p className="menu-title">

        MAIN MENU

      </p>



      {mainItems.map(

        ([id, icon, label]) => (

          <button

            key={id}

            className={`menu-item ${

              page === id

                ? "active"

                : ""

            }`}

            onClick={() =>

              setPage(id)

            }

          >

            <span className="menu-icon">

              {icon}

            </span>



            <span>{label}</span>

          </button>

        )

      )}



      <p className="menu-title account-title">

        ACCOUNT

      </p>



      <button

        className={`menu-item ${

          page === "profile"

            ? "active"

            : ""

        }`}

        onClick={() =>

          setPage("profile")

        }

      >

        <span className="menu-icon">

          👤

        </span>



        <span>Profile</span>

      </button>



      <button

        className={`menu-item ${

          page === "settings"

            ? "active"

            : ""

        }`}

        onClick={() =>

          setPage("settings")

        }

      >

        <span className="menu-icon">

          ⚙

        </span>



        <span>Settings</span>

      </button>



      <div className="sidebar-bottom">



        <div className="security-status">



          <span className="status-dot"></span>



          <div>

            <strong>

              System Online

            </strong>



            <small>

              All services operational

            </small>

          </div>



        </div>



        <button

          className="logout-btn"

          onClick={logout}

        >

          ⇥ Logout

        </button>



        <small className="version">

          VoiceShield AI v1.0

        </small>



      </div>



    </aside>

  );

}





// =====================================================

// HEADER

// =====================================================



function Header({

  page,

  user,

  alerts,

  setPage,

}) {

  const titles = {

    dashboard: [

      "Security Dashboard",

      "Monitor and analyze voice security",

    ],



    analysis: [

      "Voice Analysis",

      "Detect voice deepfakes and verify speakers",

    ],



    trusted: [

      "Trusted Voices",

      "Manage enrolled speaker identities",

    ],



    history: [

      "Analysis History",

      "Review previous security analyses",

    ],



    details: [

      "Analysis Details",

      "Detailed security assessment",

    ],



    profile: [

      "My Profile",

      "Manage your account information",

    ],



    settings: [

      "Settings",

      "Application and security preferences",

    ],



    alerts: [

      "Security Alerts",

      "Monitor suspicious voice activity",

    ],

  };



  const current =

    titles[page] ||

    titles.dashboard;



  return (

    <header className="header">



      <div>

        <h1>{current[0]}</h1>



        <p>{current[1]}</p>

      </div>



      <div className="header-right">



        <button

          className="notification-btn"

          onClick={() =>

            setPage("alerts")

          }

        >

          🔔



          {alerts.length > 0 && (

            <span>

              {alerts.length}

            </span>

          )}

        </button>



        <div

          className="profile-mini"

          onClick={() =>

            setPage("profile")

          }

        >



          {user.profileImage ? (

            <img

              src={user.profileImage}

              alt="Profile"

            />

          ) : (

            <div className="profile-avatar">

              {user.name

                ?.charAt(0)

                .toUpperCase()}

            </div>

          )}



          <div>

            <strong>

              {user.name}

            </strong>



            <small>

              Security Analyst

            </small>

          </div>



        </div>



      </div>



    </header>

  );

}





// =====================================================

// DASHBOARD

// =====================================================



function Dashboard({

  user,

  trustedVoices,

  history,

  alerts,

  setPage,

}) {

  const verifiedCount =

    history.filter(

      (x) => x.speakerVerified

    ).length;



  const spoofCount =

    history.filter(

      (x) =>

        x.deepfakeResult === "SPOOF"

    ).length;



  return (

    <div>



      <section className="hero-card">



        <div className="hero-content">



          <span className="hero-badge">

            AI-POWERED CYBERSECURITY

          </span>



          <h2>

            Protect Every Voice

          </h2>



          <p>

            Welcome back, {user.name}.

            VoiceShield AI detects AI-generated

            voice deepfakes and verifies speaker

            identities using advanced AI.

          </p>



          <button

            className="primary-btn"

            onClick={() =>

              setPage("analysis")

            }

          >

            Analyze Voice →

          </button>



        </div>



        <div className="hero-visual">

          <div className="voice-circle">

            🎙

          </div>



          <div className="wave wave-1"></div>

          <div className="wave wave-2"></div>

          <div className="wave wave-3"></div>

        </div>



      </section>





      <div className="stats-grid">



        <Stat

          icon="♙"

          title="Trusted Voices"

          value={trustedVoices.length}

          description="Registered speakers"

        />



        <Stat

          icon="◉"

          title="Total Analyses"

          value={history.length}

          description="Security analyses"

        />



        <Stat

          icon="✓"

          title="Verified"

          value={verifiedCount}

          description="Verified speakers"

        />



        <Stat

          icon="!"

          title="Spoof Detected"

          value={spoofCount}

          description="Potential deepfakes"

        />



      </div>





      <div className="dashboard-grid">



        <div className="dashboard-card">



          <CardTitle

            title="Quick Actions"

            subtitle="Start a security operation"

          />



          <div className="quick-actions">



            <Action

              icon="◉"

              title="Analyze Voice"

              text="Detect deepfake and verify speaker"

              onClick={() =>

                setPage("analysis")

              }

            />



            <Action

              icon="♙"

              title="Add Trusted Voice"

              text="Register a speaker identity"

              onClick={() =>

                setPage("trusted")

              }

            />



            <Action

              icon="◷"

              title="View History"

              text="Review previous analyses"

              onClick={() =>

                setPage("history")

              }

            />



            <Action

              icon="🔔"

              title="Security Alerts"

              text="View suspicious activity"

              onClick={() =>

                setPage("alerts")

              }

            />



          </div>



        </div>





        <div className="dashboard-card">



          <CardTitle

            title="AI Detection Pipeline"

            subtitle="Current model status"

          />



          <Model

            name="ECAPA-TDNN"

            purpose="Speaker Verification"

            status="READY"

          />



          <Model

            name="Wav2Vec2"

            purpose="Deepfake Detection"

            status="READY"

          />



          <Model

            name="Risk Engine"

            purpose="Security Risk Analysis"

            status="READY"

          />



          <Model

            name="MongoDB"

            purpose="Voice Embedding Storage"

            status="CONNECTED"

          />



        </div>



      </div>





      <div className="security-banner">



        <div className="security-banner-icon">

          🛡

        </div>



        <div>

          <strong>

            VoiceShield Security Status

          </strong>



          <p>

            AI detection engine, speaker

            verification and security services

            are ready for analysis.

          </p>

        </div>



      </div>





      {alerts.length > 0 && (

        <div className="dashboard-card recent-alerts">



          <CardTitle

            title="Recent Security Alerts"

            subtitle="Latest suspicious activity"

          />



          {alerts.slice(0, 3).map(

            (alert) => (

              <div

                className="alert-row"

                key={alert.id}

              >

                <span className="alert-dot"></span>



                <div>

                  <strong>

                    {alert.title}

                  </strong>



                  <p>

                    {alert.message}

                  </p>

                </div>



                <small>

                  {alert.date}

                </small>

              </div>

            )

          )}



        </div>

      )}



    </div>

  );

}





// =====================================================

// STAT

// =====================================================



function Stat({

  icon,

  title,

  value,

  description,

}) {

  return (

    <div className="stat-card">



      <div className="stat-icon">

        {icon}

      </div>



      <div>

        <span>{title}</span>



        <strong>{value}</strong>



        <small>

          {description}

        </small>

      </div>



    </div>

  );

}





// =====================================================

// ACTION

// =====================================================



function Action({

  icon,

  title,

  text,

  onClick,

}) {

  return (

    <button

      className="action-card"

      onClick={onClick}

    >

      <div className="action-icon">

        {icon}

      </div>



      <div>

        <strong>{title}</strong>

        <span>{text}</span>

      </div>



      <b>→</b>

    </button>

  );

}





// =====================================================

// CARD TITLE

// =====================================================



function CardTitle({

  title,

  subtitle,

}) {

  return (

    <div className="card-header">

      <h3>{title}</h3>

      <p>{subtitle}</p>

    </div>

  );

}





// =====================================================

// MODEL

// =====================================================



function Model({

  name,

  purpose,

  status,

}) {

  return (

    <div className="model-item">



      <div className="model-icon">

        AI

      </div>



      <div className="model-info">



        <strong>{name}</strong>



        <span>{purpose}</span>



      </div>



      <span className="model-status ready">

        {status}

      </span>



    </div>

  );

}





// =====================================================

// VOICE ANALYSIS

// =====================================================



function VoiceAnalysis({

  trustedVoices,

  addAnalysis,

}) {

  const [file, setFile] =

    useState(null);



  const [recording, setRecording] =

    useState(false);



  const [result, setResult] =

    useState(null);



  const mediaRecorder =

    useRef(null);



  const chunks =

    useRef([]);



  const startRecording =

    async () => {

      try {

        const stream =

          await navigator.mediaDevices.getUserMedia(

            { audio: true }

          );



        mediaRecorder.current =

          new MediaRecorder(stream);



        chunks.current = [];



        mediaRecorder.current.ondataavailable =

          (event) => {

            if (event.data.size > 0) {

              chunks.current.push(

                event.data

              );

            }

          };



        mediaRecorder.current.onstop =

          () => {

            const blob =

              new Blob(

                chunks.current,

                {

                  type: "audio/webm",

                }

              );



            const recordedFile =

              new File(

                [blob],

                "recorded_voice.webm",

                {

                  type: "audio/webm",

                }

              );



            setFile(recordedFile);



            stream

              .getTracks()

              .forEach((track) =>

                track.stop()

              );

          };



        mediaRecorder.current.start();



        setRecording(true);

      } catch {

        alert(

          "Microphone access was not allowed."

        );

      }

    };



  const stopRecording = () => {

    if (

      mediaRecorder.current &&

      recording

    ) {

      mediaRecorder.current.stop();

      setRecording(false);

    }

  };



  const analyze = async () => {
    if (!file) {
      alert("Upload audio first.");
      return;
    }

    const extension = file.name.split(".").pop().toLowerCase();
    if (!["wav", "flac"].includes(extension)) {
      alert("Please upload a WAV or FLAC file for AI analysis.");
      return;
    }

    try {
      setResult(null);
      const formData = new FormData();
      formData.append("audio", file);

      const response = await fetch("http://127.0.0.1:8000/analyze-voice", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Voice analysis failed.");
      }

      const speaker = data.speaker_verification?.speaker || "Unknown Speaker";
      const speakerVerified = data.speaker_verification?.result === "Verified";
      const similarityScore = data.speaker_verification?.similarity_score ?? 0;
      const deepfakeResult = data.deepfake_detection?.result === "Bonafide" ? "BONAFIDE" : "SPOOF";
      const bonafideProbability = data.deepfake_detection?.bonafide_probability ?? 0;
      const spoofProbability = data.deepfake_detection?.spoof_probability ?? 0;
      const confidence = Math.max(bonafideProbability, spoofProbability) * 100;
      const riskScore = data.risk_analysis?.risk_score ?? 0;
      const riskLevel = (data.risk_analysis?.risk_level || "Low").toUpperCase();

      const analysis = addAnalysis({
        fileName: file.name,
        speaker,
        speakerVerified,
        similarityScore: Number(similarityScore.toFixed(4)),
        deepfakeResult,
        confidence: Number(confidence.toFixed(2)),
        riskScore,
        riskLevel,
        bonafideProbability: Number((bonafideProbability * 100).toFixed(2)),
        spoofProbability: Number((spoofProbability * 100).toFixed(2)),
        finalResult: data.final_result,
        analysisId: data.analysis_id,
      });

      setResult(analysis);
    } catch (error) {
      console.error("Voice analysis error:", error);
      alert(error.message || "Unable to connect to VoiceShield AI backend.");
    }
  };

  return (

    <div>



      <PageIntro

        title="Voice Security Analysis"

        text="Upload or record an audio sample to verify the speaker and detect AI-generated voice content."

      />



      <div className="analysis-layout">



        <div className="upload-card">



          <CardTitle

            title="Audio Input"

            subtitle="Upload a recording or use your microphone"

          />



          <label className="upload-box">



            <input

              type="file"

              accept="audio/*"

              onChange={(e) =>

                setFile(

                  e.target.files[0]

                )

              }

            />



            <div className="upload-icon">

              📁

            </div>



            <strong>

              {file

                ? file.name

                : "Choose audio file"}

            </strong>



            <span>

              WAV, MP3, FLAC and other

              audio formats

            </span>



          </label>





          <div className="or-divider">

            OR

          </div>





          <div className="record-panel">



            <div className="record-icon">

              🎙

            </div>



            <h3>

              {recording

                ? "Recording..."

                : "Record Voice"}

            </h3>



            <p>

              Use your microphone for

              live voice analysis.

            </p>



            {recording ? (

              <button

                className="record-btn stop"

                onClick={stopRecording}

              >

                ■ Stop Recording

              </button>

            ) : (

              <button

                className="record-btn"

                onClick={startRecording}

              >

                ● Start Recording

              </button>

            )}



          </div>





          <button

            className="analyze-btn"

            onClick={analyze}

          >

            Analyze Voice

          </button>



        </div>





        <div className="result-card">



          <CardTitle

            title="Security Result"

            subtitle="AI analysis output"

          />



          {!result ? (

            <Empty

              icon="◉"

              title="No Analysis Yet"

              text="Upload or record audio and start the analysis."

            />

          ) : (

            <AnalysisResult

              result={result}

            />

          )}



        </div>



      </div>



    </div>

  );

}





// =====================================================

// ANALYSIS RESULT

// =====================================================



function AnalysisResult({

  result,

}) {

  return (

    <div>



      <div

        className={`risk-result ${

          result.riskLevel.toLowerCase()

        }`}

      >



        <div className="risk-score">

          {result.riskScore}

        </div>



        <div>

          <span>

            Risk Score

          </span>



          <strong>

            {result.riskLevel}

          </strong>

        </div>



      </div>





      <div className="result-grid">



        <ResultBox

          label="Speaker"

          value={result.speaker}

        />



        <ResultBox

          label="Speaker Verification"

          value={

            result.speakerVerified

              ? "VERIFIED"

              : "NOT VERIFIED"

          }

          success={

            result.speakerVerified

          }

        />



        <ResultBox

          label="Deepfake Detection"

          value={

            result.deepfakeResult

          }

          success={

            result.deepfakeResult ===

            "BONAFIDE"

          }

        />



        <ResultBox

          label="Confidence"

          value={`${result.confidence}%`}

        />



        <ResultBox

          label="Similarity"

          value={result.similarityScore}

        />



      </div>





      <div className="confidence-section">



        <div className="confidence-header">

          <span>

            Detection Confidence

          </span>



          <strong>

            {result.confidence}%

          </strong>

        </div>



        <div className="progress-bar">

          <div

            className="progress-fill"

            style={{

              width:

                `${result.confidence}%`,

            }}

          ></div>

        </div>



      </div>



    </div>

  );

}





// =====================================================

// RESULT BOX

// =====================================================



function ResultBox({

  label,

  value,

  success,

}) {

  return (

    <div className="result-item">



      <span>{label}</span>



      <strong

        className={

          success

            ? "success-text"

            : ""

        }

      >

        {value}

      </strong>



    </div>

  );

}





// =====================================================

// TRUSTED VOICES

// =====================================================



function TrustedVoices({

  trustedVoices,

  addTrustedVoice,

  updateTrustedVoice,

  deleteTrustedVoice,

}) {

  const [editing, setEditing] =

    useState(null);



  const [name, setName] =

    useState("");



  const [relation, setRelation] =

    useState("");



  const [recording, setRecording] =

    useState(false);



  const [audioFile, setAudioFile] =

    useState(null);



  const mediaRecorder =

    useRef(null);



  const chunks =

    useRef([]);



  const [profileImage, setProfileImage] =

    useState("");



  const startRecording =

    async () => {

      try {

        const stream =

          await navigator.mediaDevices.getUserMedia(

            { audio: true }

          );



        mediaRecorder.current =

          new MediaRecorder(stream);



        chunks.current = [];



        mediaRecorder.current.ondataavailable =

          (event) => {

            if (event.data.size > 0) {

              chunks.current.push(

                event.data

              );

            }

          };



        mediaRecorder.current.onstop =

          () => {

            const blob =

              new Blob(

                chunks.current,

                {

                  type: "audio/webm",

                }

              );



            setAudioFile(

              new File(

                [blob],

                "trusted_voice.webm",

                {

                  type: "audio/webm",

                }

              )

            );



            stream

              .getTracks()

              .forEach((track) =>

                track.stop()

              );

          };



        mediaRecorder.current.start();



        setRecording(true);

      } catch {

        alert(

          "Microphone permission is required."

        );

      }

    };



  const stopRecording = () => {

    if (

      mediaRecorder.current &&

      recording

    ) {

      mediaRecorder.current.stop();

      setRecording(false);

    }

  };



  const chooseProfileImage =

    (event) => {

      const selected =

        event.target.files[0];



      if (!selected) return;



      const reader =

        new FileReader();



      reader.onload = () =>

        setProfileImage(

          reader.result

        );



      reader.readAsDataURL(

        selected

      );

    };



  const add = () => {

    if (!name.trim()) {

      alert(

        "Enter speaker name."

      );

      return;

    }



    if (!audioFile) {

      alert(

        "Record or upload a voice."

      );

      return;

    }



    addTrustedVoice({

      name,

      relation:

        relation || "Not specified",

      fileName: audioFile.name,

      audioUrl:

        URL.createObjectURL(

          audioFile

        ),

      profileImage,

    });



    setName("");

    setRelation("");

    setAudioFile(null);

    setProfileImage("");

  };



  const beginEdit = (voice) => {

    setEditing(voice);

    setName(voice.name);

    setRelation(voice.relation);

    setProfileImage(

      voice.profileImage || ""

    );

    setAudioFile(null);

  };



  const saveEdit = () => {

    if (!editing) return;



    const updated = {

      ...editing,

      name,

      relation,

      profileImage,

      fileName:

        audioFile?.name ||

        editing.fileName,

      audioUrl:

        audioFile

          ? URL.createObjectURL(

              audioFile

            )

          : editing.audioUrl,

    };



    updateTrustedVoice(

      updated

    );



    setEditing(null);

    setName("");

    setRelation("");

    setAudioFile(null);

    setProfileImage("");

  };



  return (

    <div>



      <PageIntro

        title="Trusted Voices"

        text="Enroll and manage trusted speaker identities used by the speaker verification system."

      />



      <div className="trusted-layout">



        <div className="enrollment-card">



          <CardTitle

            title={

              editing

                ? "Edit Trusted Voice"

                : "Add Trusted Voice"

            }

            subtitle="Speaker enrollment"

          />





          <div className="photo-upload">



            <div className="speaker-photo">



              {profileImage ? (

                <img

                  src={profileImage}

                  alt="Speaker"

                />

              ) : (

                "👤"

              )}



            </div>



            <label className="secondary-btn">



              Change Photo



              <input

                type="file"

                accept="image/*"

                onChange={

                  chooseProfileImage

                }

              />



            </label>



          </div>





          <div className="form-group">



            <label>

              Speaker Name

            </label>



            <input

              type="text"

              placeholder="Example: Father"

              value={name}

              onChange={(e) =>

                setName(

                  e.target.value

                )

              }

            />



          </div>





          <div className="form-group">



            <label>

              Relationship / Role

            </label>



            <input

              type="text"

              placeholder="Example: Family"

              value={relation}

              onChange={(e) =>

                setRelation(

                  e.target.value

                )

              }

            />



          </div>





          <div className="record-panel small">



            <div className="record-icon">

              🎙

            </div>



            <h3>

              Voice Enrollment

            </h3>



            <p>

              Record a clear voice sample

              for speaker verification.

            </p>



            {recording ? (

              <button

                className="record-btn stop"

                onClick={stopRecording}

              >

                ■ Stop Recording

              </button>

            ) : (

              <button

                className="record-btn"

                onClick={

                  startRecording

                }

              >

                ● Start Recording

              </button>

            )}



          </div>





          <label className="voice-upload">



            <input

              type="file"

              accept="audio/*"

              onChange={(e) =>

                setAudioFile(

                  e.target.files[0]

                )

              }

            />



            📁

            {audioFile

              ? audioFile.name

              : "Or upload voice recording"}



          </label>





          {audioFile && (

            <div className="selected-file">

              🎵 {audioFile.name}

            </div>

          )}





          {editing ? (

            <div className="two-buttons">



              <button

                className="secondary-action"

                onClick={() =>

                  setEditing(null)

                }

              >

                Cancel

              </button>



              <button

                className="add-voice-btn"

                onClick={saveEdit}

              >

                Save Changes

              </button>



            </div>

          ) : (

            <button

              className="add-voice-btn"

              onClick={add}

            >

              + Add Trusted Voice

            </button>

          )}





          <div className="enrollment-note">



            <strong>

              🔒 Secure Enrollment

            </strong>



            <p>

              The recording will later be

              processed using ECAPA-TDNN

              to generate a speaker embedding

              for MongoDB storage.

            </p>



          </div>



        </div>





        <div className="voices-list-card">



          <CardTitle

            title="Registered Voices"

            subtitle={`${trustedVoices.length} trusted speaker(s)`}

          />



          {trustedVoices.length === 0 ? (

            <Empty

              icon="♙"

              title="No Trusted Voices"

              text="Add your first trusted speaker using the enrollment form."

            />

          ) : (

            <div className="voice-list">



              {trustedVoices.map(

                (voice) => (

                  <div

                    className="trusted-voice"

                    key={voice.id}

                  >



                    <div className="voice-avatar">



                      {voice.profileImage ? (

                        <img

                          src={

                            voice.profileImage

                          }

                          alt={

                            voice.name

                          }

                        />

                      ) : (

                        voice.name

                          .charAt(0)

                          .toUpperCase()

                      )}



                    </div>





                    <div className="voice-details">



                      <strong>

                        {voice.name}

                      </strong>



                      <span>

                        {voice.relation}

                      </span>



                      <small>

                        🎵{" "}

                        {voice.fileName}

                      </small>



                      <small>

                        Added:{" "}

                        {voice.dateAdded}

                      </small>



                      <small className="embedding-ready">

                        ● Embedding:{" "}

                        {voice.embeddingStatus}

                      </small>



                    </div>





                    <div className="voice-actions">



                      {voice.audioUrl && (

                        <audio

                          controls

                          src={

                            voice.audioUrl

                          }

                        />

                      )}



                      <button

                        className="edit-btn"

                        onClick={() =>

                          beginEdit(

                            voice

                          )

                        }

                      >

                        ✏ Edit

                      </button>



                      <button

                        className="delete-btn"

                        onClick={() =>

                          deleteTrustedVoice(

                            voice.id

                          )

                        }

                      >

                        🗑

                      </button>



                    </div>



                  </div>

                )

              )}



            </div>

          )}



        </div>



      </div>



    </div>

  );

}





// =====================================================

// HISTORY

// =====================================================



function AnalysisHistory({

  history,

  setSelectedAnalysis,

  setPage,

}) {

  return (

    <div>



      <PageIntro

        title="Analysis History"

        text="Review all previous voice security analyses."

      />



      <div className="history-card">



        {history.length === 0 ? (

          <Empty

            icon="◷"

            title="No Analysis History"

            text="Completed voice analyses will appear here."

          />

        ) : (



          <div className="table-container">



            <table>



              <thead>



                <tr>

                  <th>Audio</th>

                  <th>Speaker</th>

                  <th>Verification</th>

                  <th>Deepfake</th>

                  <th>Confidence</th>

                  <th>Risk</th>

                  <th>Details</th>

                </tr>



              </thead>



              <tbody>



                {history.map(

                  (item) => (

                    <tr key={item.id}>



                      <td>

                        {item.fileName}

                      </td>



                      <td>

                        {item.speaker}

                      </td>



                      <td>

                        <Badge

                          success={

                            item.speakerVerified

                          }

                          text={

                            item.speakerVerified

                              ? "Verified"

                              : "Not Verified"

                          }

                        />

                      </td>



                      <td>

                        <Badge

                          success={

                            item.deepfakeResult ===

                            "BONAFIDE"

                          }

                          text={

                            item.deepfakeResult

                          }

                        />

                      </td>



                      <td>

                        {item.confidence}%

                      </td>



                      <td>

                        <span

                          className={`risk-badge ${item.riskLevel.toLowerCase()}`}

                        >

                          {item.riskLevel}

                        </span>

                      </td>



                      <td>



                        <button

                          className="details-btn"

                          onClick={() => {

                            setSelectedAnalysis(

                              item

                            );



                            setPage(

                              "details"

                            );

                          }}

                        >

                          View

                        </button>



                      </td>



                    </tr>

                  )

                )}



              </tbody>



            </table>



          </div>



        )}



      </div>



    </div>

  );

}





// =====================================================

// ANALYSIS DETAILS

// =====================================================



function AnalysisDetails({

  analysis,

  setPage,

}) {

  if (!analysis) {

    return (

      <Empty

        icon="?"

        title="No Analysis Selected"

        text="Select an analysis from the history page."

      />

    );

  }



  return (

    <div>



      <button

        className="back-btn"

        onClick={() =>

          setPage("history")

        }

      >

        ← Back to History

      </button>





      <PageIntro

        title="Analysis Details"

        text={`Detailed report for ${analysis.fileName}`}

      />





      <div className="report-grid">



        <div className="report-card">



          <h3>

            Audio Information

          </h3>



          <InfoRow

            label="File"

            value={

              analysis.fileName

            }

          />



          <InfoRow

            label="Analysis Time"

            value={

              analysis.date

            }

          />



          <InfoRow

            label="Confidence"

            value={`${analysis.confidence}%`}

          />



        </div>





        <div className="report-card">



          <h3>

            Speaker Verification

          </h3>



          <InfoRow

            label="Speaker"

            value={

              analysis.speaker

            }

          />



          <InfoRow

            label="Verification"

            value={

              analysis.speakerVerified

                ? "VERIFIED"

                : "NOT VERIFIED"

            }

          />



          <InfoRow

            label="Similarity"

            value={

              analysis.similarityScore

            }

          />



        </div>





        <div className="report-card">



          <h3>

            Deepfake Detection

          </h3>



          <InfoRow

            label="Classification"

            value={

              analysis.deepfakeResult

            }

          />



          <InfoRow

            label="Confidence"

            value={`${analysis.confidence}%`}

          />



          <InfoRow

            label="Model"

            value="Wav2Vec2"

          />



        </div>





        <div className="report-card">



          <h3>

            Risk Analysis

          </h3>



          <div className="large-risk">

            {analysis.riskScore}

          </div>



          <strong>

            {analysis.riskLevel} RISK

          </strong>



          <p>

            Risk is calculated using the

            speaker verification and deepfake

            detection results.

          </p>



        </div>



      </div>





      <div className="report-card explanation-card">



        <h3>

          Security Assessment

        </h3>



        {analysis.riskLevel ===

        "LOW" ? (

          <p>

            The speaker was successfully

            verified and the audio was

            classified as bonafide.

          </p>

        ) : (

          <p>

            The audio requires additional

            verification because the speaker

            could not be reliably trusted or

            suspicious synthetic speech was

            detected.

          </p>

        )}



        <button

          className="primary-btn dark"

          onClick={() =>

            window.print()

          }

        >

          📄 Export / Print Report

        </button>



      </div>



    </div>

  );

}





// =====================================================

// PROFILE

// =====================================================



function ProfilePage({

  user,

  updateProfile,

}) {

  const [name, setName] =

    useState(user.name);



  const [email, setEmail] =

    useState(user.email);



  const [image, setImage] =

    useState(

      user.profileImage || ""

    );



  const chooseImage =

    (event) => {

      const file =

        event.target.files[0];



      if (!file) return;



      const reader =

        new FileReader();



      reader.onload = () =>

        setImage(

          reader.result

        );



      reader.readAsDataURL(file);

    };



  const save = () => {

    updateProfile({

      name,

      email,

      profileImage: image,

    });



    alert(

      "Profile updated successfully."

    );

  };



  return (

    <div>



      <PageIntro

        title="My Profile"

        text="Manage your VoiceShield account."

      />





      <div className="profile-page-card">



        <div className="profile-photo-section">



          <div className="large-profile-photo">



            {image ? (

              <img

                src={image}

                alt="Profile"

              />

            ) : (

              name

                ?.charAt(0)

                .toUpperCase()

            )}



          </div>



          <label className="secondary-btn">



            Change Profile Photo



            <input

              type="file"

              accept="image/*"

              onChange={

                chooseImage

              }

            />



          </label>



        </div>





        <div className="profile-form">



          <h3>

            Personal Information

          </h3>



          <div className="form-group">



            <label>

              Full Name

            </label>



            <input

              value={name}

              onChange={(e) =>

                setName(

                  e.target.value

                )

              }

            />



          </div>



          <div className="form-group">



            <label>

              Email Address

            </label>



            <input

              value={email}

              onChange={(e) =>

                setEmail(

                  e.target.value

                )

              }

            />



          </div>



          <button

            className="add-voice-btn"

            onClick={save}

          >

            Save Profile Changes

          </button>



        </div>



      </div>



    </div>

  );

}





// =====================================================

// SETTINGS

// =====================================================



function SettingsPage({

  settings,

  setSettings,

  logout,

  setHistory,

}) {

  return (

    <div>



      <PageIntro

        title="Settings"

        text="Configure application and security preferences."

      />





      <div className="settings-card">



        <h3>

          Notifications

        </h3>



        <SettingToggle

          title="Security Notifications"

          text="Receive alerts for suspicious voice activity."

          value={

            settings.notifications

          }

          onChange={(value) =>

            setSettings({

              ...settings,

              notifications:

                value,

            })

          }

        />





        <h3>

          Privacy

        </h3>



        <SettingToggle

          title="Auto-delete Audio"

          text="Automatically remove temporary audio after analysis."

          value={

            settings.autoDeleteAudio

          }

          onChange={(value) =>

            setSettings({

              ...settings,

              autoDeleteAudio:

                value,

            })

          }

        />



        <SettingToggle

          title="Save Analysis History"

          text="Keep completed analysis results in the dashboard."

          value={

            settings.saveHistory

          }

          onChange={(value) =>

            setSettings({

              ...settings,

              saveHistory:

                value,

            })

          }

        />





        <h3>

          Appearance

        </h3>



        <SettingToggle

          title="Dark Mode"

          text="Use a dark interface."

          value={

            settings.darkMode

          }

          onChange={(value) =>

            setSettings({

              ...settings,

              darkMode: value,

            })

          }

        />





        <h3>

          Account

        </h3>



        <button

          className="danger-action"

          onClick={() => {

            if (

              window.confirm(

                "Clear all analysis history?"

              )

            ) {

              setHistory([]);

            }

          }}

        >

          Clear Analysis History

        </button>



        <button

          className="logout-large"

          onClick={logout}

        >

          Logout

        </button>



      </div>



    </div>

  );

}





// =====================================================

// SETTING TOGGLE

// =====================================================



function SettingToggle({

  title,

  text,

  value,

  onChange,

}) {

  return (

    <div className="setting-row">



      <div>

        <strong>

          {title}

        </strong>



        <p>

          {text}

        </p>

      </div>



      <button

        className={`toggle ${

          value ? "on" : ""

        }`}

        onClick={() =>

          onChange(!value)

        }

      >

        <span></span>

      </button>



    </div>

  );

}





// =====================================================

// ALERTS

// =====================================================



function AlertsPage({

  alerts,

  setAlerts,

}) {

  return (

    <div>



      <PageIntro

        title="Security Alerts"

        text="Monitor suspicious voice activity and security events."

      />



      <div className="alerts-card">



        {alerts.length === 0 ? (

          <Empty

            icon="✓"

            title="No Security Alerts"

            text="Your system has no recent suspicious activity."

          />

        ) : (



          alerts.map(

            (alert) => (

              <div

                className="full-alert"

                key={alert.id}

              >



                <div className="alert-large-icon">

                  ⚠

                </div>



                <div>



                  <strong>

                    {alert.title}

                  </strong>



                  <p>

                    {alert.message}

                  </p>



                  <small>

                    {alert.date}

                  </small>



                </div>



              </div>

            )

          )



        )}



        {alerts.length > 0 && (

          <button

            className="clear-alerts"

            onClick={() =>

              setAlerts([])

            }

          >

            Clear Alerts

          </button>

        )}



      </div>



    </div>

  );

}





// =====================================================

// PAGE INTRO

// =====================================================



function PageIntro({

  title,

  text,

}) {

  return (

    <section className="page-intro">



      <h2>{title}</h2>



      <p>{text}</p>



    </section>

  );

}





// =====================================================

// EMPTY

// =====================================================



function Empty({

  icon,

  title,

  text,

}) {

  return (

    <div className="empty-state">



      <div className="empty-icon">

        {icon}

      </div>



      <h3>

        {title}

      </h3>



      <p>

        {text}

      </p>



    </div>

  );

}





// =====================================================

// BADGE

// =====================================================



function Badge({

  success,

  text,

}) {

  return (

    <span

      className={

        success

          ? "table-badge verified"

          : "table-badge danger"

      }

    >

      {text}

    </span>

  );

}





// =====================================================

// INFO ROW

// =====================================================



function InfoRow({

  label,

  value,

}) {

  return (

    <div className="info-row">



      <span>

        {label}

      </span>



      <strong>

        {value}

      </strong>



    </div>

  );

}





export default App;