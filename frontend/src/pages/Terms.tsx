import "./Privacy.css";

import React from "react";
import { useAuth } from "@/contexts/AuthContext";

const Terms: React.FC = () => {
  const { user } = useAuth();
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        Terms of Service for Landon Kleinbrodt Apps
      </h1>
      {user && <p className="mb-4">Hello {user.name}!</p>}
      <p className="text-gray-600 mb-4">Last updated: July 16, 2025</p>

      <div className="space-y-6">
        <section>
          <p className="mb-4">
            These Terms of Service (“Terms”) govern your use of any mobile apps
            or websites provided by Landon Kleinbrodt (“I”, “me”, “my”). By
            using my apps or website, you agree to these Terms.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">1. Use of my apps</h2>
          <p className="mb-4">
            You may use my apps for personal, non-commercial purposes only, in
            accordance with these Terms and all applicable laws.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">
            2. Intellectual property
          </h2>
          <p className="mb-4">
            All content, code, and materials in my apps and website are owned by
            me or my licensors. You may not copy, modify, distribute, or reverse
            engineer any part of them without my permission.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">3. Disclaimer</h2>
          <p className="mb-4">
            My apps and website are provided “as is”. I do not guarantee they
            will always be available, secure, or error-free. Use them at your
            own risk.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">
            4. Limitation of liability
          </h2>
          <p className="mb-4">
            To the fullest extent allowed by law, I am not liable for any
            indirect, incidental, or consequential damages arising out of your
            use of my apps or website.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">5. Third-party links</h2>
          <p className="mb-4">
            My apps or website may contain links to third-party services I don’t
            control. I’m not responsible for those services.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">6. Changes</h2>
          <p className="mb-4">
            I may update these Terms from time to time. If I make material
            changes, I’ll post them on my website and update the “Last updated”
            date. By continuing to use my services, you accept any changes.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">7. Governing law</h2>
          <p className="mb-4">
            These Terms are governed by the laws of California, USA.
          </p>
        </section>

        <hr />

        <section>
          <h2 className="text-2xl font-semibold mb-4">8. Contact</h2>
          <p className="mb-4">Questions? Reach me at:</p>
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
      </div>
    </div>
  );
};

export default Terms;
