import { ArrowLeft, HelpCircle, Home, Mail } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";

function Help() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/20 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-2xl"
      >
        <Card className="border-0 shadow-2xl bg-card/80 backdrop-blur-sm">
          <CardHeader className="text-center pb-4">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="flex justify-center mb-4"
            >
              <div className="relative">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary/20 to-primary/40 flex items-center justify-center">
                  <HelpCircle className="w-12 h-12 text-primary" />
                </div>
                <motion.div
                  animate={{
                    scale: [1, 1.1, 1],
                    opacity: [0.5, 0.8, 0.5],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                  className="absolute inset-0 rounded-full bg-gradient-to-br from-primary/30 to-transparent"
                />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <CardTitle className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-br from-primary to-primary/60">
                Need Assistance?
              </CardTitle>
              <CardDescription className="text-lg text-muted-foreground">
                We're here to help you make the most of your experience!
              </CardDescription>
            </motion.div>
          </CardHeader>

          <CardContent className="text-center space-y-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="space-y-4"
            >
              {user && (
                <p className="text-muted-foreground text-lg">
                  Hello {user.name}! 👋
                </p>
              )}
              <p className="text-muted-foreground text-lg leading-relaxed">
                Whether you have questions about the app, need technical
                support, or want to share feedback, our team is ready to assist
                you.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.5 }}
              className="space-y-4"
            >
              <Button
                asChild
                size="lg"
                className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 w-full sm:w-auto"
              >
                <a
                  href="mailto:landon@coyote-ai.com"
                  className="flex items-center gap-2"
                >
                  <Mail className="w-4 h-4" />
                  Contact Support
                </a>
              </Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.5 }}
              className="pt-4 border-t border-border/50 flex flex-col sm:flex-row gap-3 justify-center"
            >
              <Button asChild variant="ghost" size="sm">
                <Link
                  to="/"
                  className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
                >
                  <Home className="w-4 h-4" />
                  Go Home
                </Link>
              </Button>
              <Button asChild variant="ghost" size="sm">
                <Link
                  to="/"
                  className="flex items-center gap-2 text-muted-foreground hover:text-foreground"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to previous page
                </Link>
              </Button>
            </motion.div>
          </CardContent>
        </Card>

        {/* Floating elements for visual interest */}
        <motion.div
          animate={{
            y: [0, -10, 0],
            rotate: [0, 5, 0],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-20 left-10 w-4 h-4 bg-primary/20 rounded-full blur-sm"
        />
        <motion.div
          animate={{
            y: [0, 15, 0],
            rotate: [0, -5, 0],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
          className="absolute bottom-20 right-10 w-6 h-6 bg-primary/20 rounded-full blur-sm"
        />
        <motion.div
          animate={{
            y: [0, -8, 0],
            x: [0, 5, 0],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2,
          }}
          className="absolute top-1/2 left-20 w-3 h-3 bg-secondary/30 rounded-full blur-sm"
        />
      </motion.div>
    </div>
  );
}

export default Help;
