import { cn } from "@/lib/utils";

interface KeyProps {
  children: React.ReactNode;
  className?: string;
}

function Key({ children, className }: KeyProps) {
  return (
    <div
      className={cn(
        "bg-white/20 border border-white/40 rounded px-2.5 py-1.5 min-w-[20px] text-center text-sm",
        className
      )}
    >
      {children}
    </div>
  );
}

const controls = [
  {
    keys: [{ layout: "vertical", keys: ["↑", ["←", "↓", "→"]] }],
    action: "Rotate Camera",
  },
  {
    keys: [{ layout: "vertical", keys: ["W", ["A", "S", "D"]] }],
    action: "Move Camera",
  },
  {
    keys: [["Q", "E"]],
    action: "Up / Down",
  },
  {
    keys: [["Space"]],
    action: "Reset",
  },
] as const;

export function ControlsTooltip() {
  return (
    <div className="text-white font-sans w-2/6">
      <div className="flex flex-col gap-3">
        {controls.map((control, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className="flex gap-1">
              {control.keys.map((keyGroup, j) => (
                <div key={j} className="flex flex-col items-center gap-1">
                  {typeof keyGroup === "object" && "layout" in keyGroup ? (
                    <>
                      {keyGroup.keys.map((k, idx) =>
                        Array.isArray(k) ? (
                          <div key={idx} className="flex gap-1">
                            {k.map((subKey, subIdx) => (
                              <Key key={subIdx}>{subKey}</Key>
                            ))}
                          </div>
                        ) : (
                          <Key key={idx}>{k}</Key>
                        )
                      )}
                    </>
                  ) : (
                    keyGroup.map((key, idx) => <Key key={idx}>{key}</Key>)
                  )}
                </div>
              ))}
            </div>
            <span className="text-sm whitespace-nowrap">{control.action}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
