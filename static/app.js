/* PlainSpeak frontend: input -> simplify -> results -> quiz. */
(function () {
  "use strict";

  var textarea = document.getElementById("input-text");
  var charCount = document.getElementById("char-count");
  var btn = document.getElementById("simplify-btn");
  var inputError = document.getElementById("input-error");
  var results = document.getElementById("results");
  var inputCard = document.getElementById("input-card");
  var modeBanner = document.getElementById("mode-banner");

  var quizState = null;

  textarea.addEventListener("input", function () {
    charCount.textContent = textarea.value.length;
    hideError();
  });

  document.querySelectorAll("[data-sample]").forEach(function (chip) {
    chip.addEventListener("click", function () {
      fetch("/api/samples/" + chip.getAttribute("data-sample"))
        .then(function (r) { return r.json(); })
        .then(function (d) {
          textarea.value = d.text;
          charCount.textContent = d.text.length;
          hideError();
          textarea.focus();
        });
    });
  });

  // Show the demo-mode banner as soon as we know the server mode.
  fetch("/api/health")
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (d.mode === "demo") {
        modeBanner.textContent =
          "Demo mode — add an LLM key for live AI. Simplifications here are rule-based and illustrative.";
        modeBanner.classList.remove("hidden");
      }
    })
    .catch(function () {});

  function hideError() {
    inputError.classList.add("hidden");
    inputError.textContent = "";
  }

  function showError(msg) {
    inputError.textContent = msg;
    inputError.classList.remove("hidden");
  }

  function level() {
    var el = document.querySelector('input[name="level"]:checked');
    return el ? el.value : "plain";
  }

  btn.addEventListener("click", function () {
    hideError();
    var text = textarea.value.trim();
    if (text.length < 50) {
      showError("Paste at least 50 characters — a real paragraph of the confusing stuff.");
      return;
    }
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Simplifying…';

    fetch("/api/simplify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, level: level() }),
    })
      .then(function (r) {
        return r.json().then(function (d) {
          return { status: r.status, body: d };
        });
      })
      .then(function (res) {
        btn.disabled = false;
        btn.textContent = "Simplify it →";
        if (res.status !== 200) {
          showError(res.body.error || "Something went wrong. Try again.");
          return;
        }
        renderResults(res.body);
      })
      .catch(function () {
        btn.disabled = false;
        btn.textContent = "Simplify it →";
        showError("Couldn't reach the server. Is it still running?");
      });
  });

  function renderResults(d) {
    document.getElementById("simplified-text").textContent = d.simplified;

    var demoNote = document.getElementById("demo-note");
    if (d.mode === "demo") {
      demoNote.textContent =
        "Demo mode output — simplified with hand-written rules, not AI. Add an LLM key for the live version.";
      demoNote.classList.remove("hidden");
    } else {
      demoNote.classList.add("hidden");
    }

    var ul = document.getElementById("takeaways");
    ul.innerHTML = "";
    d.takeaways.forEach(function (t) {
      var li = document.createElement("li");
      li.textContent = t;
      ul.appendChild(li);
    });

    renderScores(d.readability_before, d.readability_after);

    var qNote = document.getElementById("quiz-demo-note");
    if (d.mode === "demo") {
      qNote.textContent = "Demo-mode quiz: keyword checks, not comprehension questions.";
      qNote.classList.remove("hidden");
    } else {
      qNote.classList.add("hidden");
    }
    startQuiz(d.quiz);

    inputCard.classList.add("hidden");
    results.classList.remove("hidden");
    results.scrollIntoView({ behavior: "smooth" });
  }

  function renderScores(before, after) {
    document.getElementById("grade-before").textContent = "Grade " + before.fk_grade;
    document.getElementById("label-before").textContent = before.label;
    document.getElementById("grade-after").textContent = "Grade " + after.fk_grade;
    document.getElementById("label-after").textContent = after.label;
    // Bar scale: grade 0..20 mapped to 0..100%
    document.getElementById("bar-before").style.width =
      Math.min(100, (before.fk_grade / 20) * 100) + "%";
    document.getElementById("bar-after").style.width =
      Math.min(100, (after.fk_grade / 20) * 100) + "%";
    var note = document.getElementById("score-note");
    var drop = before.fk_grade - after.fk_grade;
    if (drop > 0.5) {
      note.textContent =
        "Reading level dropped by " + drop.toFixed(1) + " grades — that's the simplification working.";
    } else if (drop < -0.5) {
      note.textContent =
        "Honest note: the rewrite scored slightly harder to read. The meaning is still plainer — scores aren't everything.";
    } else {
      note.textContent = "Reading level stayed about the same — this one was already fairly clear.";
    }
  }

  function startQuiz(questions) {
    quizState = { questions: questions, index: 0, score: 0 };
    renderQuestion();
  }

  function renderQuestion() {
    var box = document.getElementById("quiz-box");
    box.innerHTML = "";
    var st = quizState;
    if (st.index >= st.questions.length) {
      renderScore(box);
      return;
    }
    var q = st.questions[st.index];

    var prog = document.createElement("div");
    prog.className = "quiz-progress";
    prog.textContent = "Question " + (st.index + 1) + " of " + st.questions.length;
    box.appendChild(prog);

    var p = document.createElement("p");
    p.className = "quiz-q";
    p.textContent = q.question;
    box.appendChild(p);

    var opts = document.createElement("div");
    opts.className = "quiz-opts";
    q.options.forEach(function (opt, i) {
      var b = document.createElement("button");
      b.className = "quiz-opt";
      b.textContent = opt;
      b.addEventListener("click", function () { answer(i, b, opts); });
      opts.appendChild(b);
    });
    box.appendChild(opts);

    var fb = document.createElement("p");
    fb.className = "quiz-feedback hidden";
    fb.id = "quiz-feedback";
    box.appendChild(fb);
  }

  function answer(i, btnEl, optsEl) {
    var st = quizState;
    var q = st.questions[st.index];
    var correct = i === q.answer;
    if (correct) st.score++;

    Array.prototype.forEach.call(optsEl.children, function (b, j) {
      b.disabled = true;
      if (j === q.answer) b.classList.add("correct");
      else if (j === i) b.classList.add("wrong");
    });

    var fb = document.getElementById("quiz-feedback");
    fb.classList.remove("hidden");
    if (correct) {
      fb.textContent = "Right — nicely read.";
      fb.className = "quiz-feedback good";
    } else {
      fb.textContent = "Not quite — the answer was: " + q.options[q.answer];
      fb.className = "quiz-feedback bad";
    }

    var next = document.createElement("button");
    next.className = "secondary";
    next.style.marginTop = "1rem";
    next.textContent = st.index + 1 >= st.questions.length ? "See my score →" : "Next question →";
    next.addEventListener("click", function () {
      st.index++;
      renderQuestion();
    });
    document.getElementById("quiz-box").appendChild(next);
  }

  function renderScore(box) {
    var st = quizState;
    var box2 = box;
    box.innerHTML = "";
    var wrap = document.createElement("div");
    wrap.className = "quiz-score";
    var big = document.createElement("span");
    big.className = "big";
    big.textContent = st.score + "/" + st.questions.length;
    wrap.appendChild(big);
    var p = document.createElement("p");
    if (st.score === st.questions.length) p.textContent = "Perfect — you actually understood it.";
    else if (st.score >= 2) p.textContent = "Solid — the simplification did its job.";
    else p.textContent = "Worth re-reading the clear version once more.";
    wrap.appendChild(p);
    var retry = document.createElement("button");
    retry.className = "secondary";
    retry.textContent = "↺ Retake the quiz";
    retry.addEventListener("click", function () {
      st.index = 0; st.score = 0; renderQuestion();
    });
    wrap.appendChild(retry);
    box2.appendChild(wrap);
  }

  document.getElementById("reset-btn").addEventListener("click", function () {
    results.classList.add("hidden");
    inputCard.classList.remove("hidden");
    textarea.value = "";
    charCount.textContent = "0";
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
})();
