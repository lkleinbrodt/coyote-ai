import "./Privacy.css";

import React from "react";
import { useAuth } from "@/contexts/AuthContext";

const Privacy: React.FC = () => {
  const { user } = useAuth();
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        Privacy Policy for Landon Kleinbrodt Apps
      </h1>
      {user && <p className="mb-4">Hello {user.name}!</p>}
      <p className="text-gray-600 mb-4">Last updated: July 16, 2025</p>

      <div className="space-y-6">
        <section>
          <p className="mb-4">
            This Privacy Policy explains how I (“Landon Kleinbrodt”, “I”, “me”,
            or “my”) collect, use, and share your information when you use any
            of my apps or my website at{" "}
            <a
              href="https://landonkleinbrodt.com"
              className="text-blue-600 underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              https://landonkleinbrodt.com
            </a>
            . By using my services, you agree to this policy.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">
            1. App-Specific Privacy Policies
          </h2>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-semibold text-green-800 mb-2">
              Slate iOS App
            </h3>
            <p className="text-green-700 mb-2">
              The Slate iOS app collects <strong>zero data whatsoever</strong>.
              It operates entirely offline and does not collect, store, or
              transmit any personal information, usage data, or analytics. This
              app is completely privacy-focused with no data collection.
            </p>
            <p className="text-green-700 text-sm">
              <strong>Data Collection:</strong> None
              <br />
              <strong>Data Storage:</strong> None
              <br />
              <strong>Data Sharing:</strong> None
              <br />
              <strong>Analytics:</strong> None
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">
              SpeechWise & Web Applications
            </h3>
            <p className="text-blue-700 mb-2">
              These applications may collect and process data as described in
              the general privacy policy below.
            </p>
            <p className="text-blue-700 text-sm">
              <strong>Data Collection:</strong> Personal data, usage data,
              cookies
              <br />
              <strong>Data Storage:</strong> As needed for service provision
              <br />
              <strong>Data Sharing:</strong> With service providers, as required
              by law
              <br />
              <strong>Analytics:</strong> Usage analytics for service
              improvement
            </p>
          </div>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">
            2. General Privacy Policy
          </h2>
          <p className="mb-4 text-sm text-gray-600">
            <em>
              This section applies to all other apps not specifically mentioned
              above.
            </em>
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">3. What I collect</h2>
          <ul className="list-disc pl-6 space-y-2 mb-4">
            <li>
              <strong>Personal Data:</strong> e.g., name, email address if you
              provide it.
            </li>
            <li>
              <strong>Usage Data:</strong> e.g., IP address, device type, app
              interactions.
            </li>
            <li>
              <strong>Cookies/Tracking Data (for the website):</strong> to
              understand usage and improve my services.
            </li>
          </ul>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">
            4. How I use your data
          </h2>
          <ul className="list-disc pl-6 space-y-2 mb-4">
            <li>Provide, maintain, and improve my apps and website.</li>
            <li>Communicate with you, if you reach out.</li>
            <li>Comply with legal obligations.</li>
            <li>Analyze usage to improve features and performance.</li>
            <li>Send you updates or marketing, if you opt in.</li>
          </ul>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">5. Sharing your data</h2>
          <ul className="list-disc pl-6 space-y-2 mb-4">
            <li>
              With trusted service providers (e.g., analytics tools) to help run
              the services.
            </li>
            <li>If required by law or to protect rights and safety.</li>
            <li>
              In connection with a business transfer (if I sell or transfer part
              of my business).
            </li>
            <li>With your consent.</li>
          </ul>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">
            6. Data storage & security
          </h2>
          <p className="mb-4">
            I keep your data only as long as needed for the purposes above. I
            use reasonable measures to protect it, but no system is 100% secure.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">7. Your choices</h2>
          <ul className="list-disc pl-6 space-y-2 mb-4">
            <li>You can usually manage cookies in your browser settings.</li>
            <li>
              You may contact me to access, correct, or delete your data (unless
              I'm legally required to keep it).
            </li>
          </ul>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">8. Children's privacy</h2>
          <p className="mb-4">
            My services are not intended for children under 13. I do not
            knowingly collect personal data from children under 13. If you think
            your child has provided personal data, please contact me.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">9. External links</h2>
          <p className="mb-4">
            My services may link to other sites I don't control. Please review
            their privacy policies — I'm not responsible for them.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">10. Changes</h2>
          <p className="mb-4">
            I may update this Privacy Policy from time to time. Changes will be
            posted here with an updated date. Please review periodically.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">11. Contact</h2>
          <p className="mb-4">Questions? Contact me:</p>
          <ul className="list-disc pl-6 space-y-2 mb-4">
            <li>
              Email:{" "}
              <a
                href="mailto:landon@coyote-ai.com"
                className="text-blue-600 underline"
              >
                landon@coyote-ai.com
              </a>
            </li>
            <li>
              Help page:{" "}
              <a
                href="https://landonkleinbrodt.com/help"
                className="text-blue-600 underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                https://landonkleinbrodt.com/help
              </a>
            </li>
          </ul>
        </section>

        <hr />

        <hr />
      </div>
    </div>
  );
};

export default Privacy;
