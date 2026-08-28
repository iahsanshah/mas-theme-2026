// Adds the tagline + social links row to the branded panel on the login page.
// Scoped to .for-login only so signup/forgot-password pages are untouched.
document.addEventListener("DOMContentLoaded", function () {
	var forLogin = document.querySelector(".for-login");
	var head = forLogin ? forLogin.querySelector(".page-card-head") : null;
	if (!forLogin || !head) return;

	// .page-card-head and .login-content.page-card are siblings directly
	// inside .for-login, which is also Frappe's full-viewport centering
	// wrapper. Wrap both in a dedicated shell so the two-panel card sizes
	// to its own content instead of inheriting .for-login's min-height.
	var card = forLogin.querySelector(".login-content.page-card");
	var shell = document.createElement("div");
	shell.className = "mas-login-shell";
	forLogin.insertBefore(shell, head);
	shell.appendChild(head);
	if (card) shell.appendChild(card);

	var heading = head.querySelector("h4");
	if (heading) heading.innerHTML = 'Login To Thru<sup class="mas-login-tm">™</sup> Software';

	var tagline = document.createElement("p");
	tagline.className = "mas-login-tagline";
	tagline.textContent = "Manage your business, all in one place.";
	head.appendChild(tagline);

	var socialLinks = [
		{
			name: "LinkedIn",
			href: "https://www.linkedin.com/company/trpl-digital-solutions/posts/?feedView=all",
			inner: '<path fill="currentColor" d="M4.98 3.5C4.98 4.88 3.88 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5ZM.5 8h4V23h-4V8Zm7.5 0h3.83v2.05h.05c.53-1 1.84-2.05 3.79-2.05C19.9 8 21 10.2 21 13.86V23h-4v-8.2c0-1.96-.04-4.47-2.73-4.47-2.73 0-3.15 2.13-3.15 4.33V23h-4V8Z"/>',
		},
		{
			name: "Website",
			href: "https://www.trpl.solutions/",
			inner:
				'<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.6"/>' +
				'<line x1="2" y1="12" x2="22" y2="12" stroke="currentColor" stroke-width="1.6"/>' +
				'<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" fill="none" stroke="currentColor" stroke-width="1.6"/>',
		},
	];

	var socialLabel = document.createElement("p");
	socialLabel.className = "mas-login-social-label";
	socialLabel.textContent = "Connect With Us";
	head.appendChild(socialLabel);

	var wrap = document.createElement("div");
	wrap.className = "mas-login-social";
	socialLinks.forEach(function (s) {
		var a = document.createElement("a");
		a.href = s.href;
		a.target = "_blank";
		a.rel = "noopener noreferrer";
		a.setAttribute("aria-label", s.name);
		a.innerHTML =
			'<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">' + s.inner + "</svg>";
		wrap.appendChild(a);
	});
	head.appendChild(wrap);
});
