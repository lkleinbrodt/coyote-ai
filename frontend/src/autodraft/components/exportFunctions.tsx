import { Document, Packer, Paragraph } from "docx";
import { Project, Prompt, Report } from "@/autodraft/types";

export function exportTxt(
  prompts: Prompt[],
  selectedProject: Project,
  selectedReport: Report
) {
  //go through each prompt and get the prompt.text and the prompt.responses[0].text
  //concatenate them like this: Prompt: \nResponse: \n\n
  //then export as a txt file

  let exportString = "";
  prompts.forEach((prompt) => {
    exportString += `${prompt.text}:\n${prompt.responses[0].text}\n\n`;
  });

  const blob = new Blob([exportString], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  //name should be ProjectName_ReportName_Date.txt
  a.download = `${selectedProject?.name}_${
    selectedReport?.name
  }_${new Date().toLocaleDateString()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  console.log("Exported");
}

export function exportDocx(
  prompts: Prompt[],
  selectedProject: Project,
  selectedReport: Report
) {
  const doc = new Document({
    sections: [
      {
        properties: {},
        children: prompts.flatMap((prompt) => [
          new Paragraph({ text: prompt.text, spacing: { before: 400 } }),
          new Paragraph({ text: prompt.responses[0].text }),
          new Paragraph({ text: "" }), // Empty paragraph for spacing
        ]),
      },
    ],
  });

  Packer.toBlob(doc).then((blob) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${selectedProject?.name}_${
      selectedReport?.name
    }_${new Date().toLocaleDateString()}.docx`;
    a.click();
    URL.revokeObjectURL(url);
    console.log("Exported");
  });
}
