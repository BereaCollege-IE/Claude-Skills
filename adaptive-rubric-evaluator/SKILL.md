---
name: adaptive-rubric-evaluator
description: Evaluate artifacts (assessment reports, student projects, accreditation documents) using provided rubrics. Auto-detects context, adapts feedback tone and depth, and produces structured outputs for integration with gradebook systems, email drafts, and report generation tools.
---

# Adaptive Rubric Evaluator

## Purpose
Evaluate artifacts (assessment reports, student projects, accreditation documents) using provided rubrics. Auto-detects context, adapts feedback tone and depth, and produces structured outputs for integration with gradebook systems, email drafts, and report generation tools.

## When to Use This Skill
Claude should use this skill when the user:
- Asks to evaluate, assess, grade, review, or provide feedback on an artifact using a rubric
- Mentions applying rubric criteria to student work, reports, or documents
- Requests both formative and summative feedback
- Wants structured evaluation data for downstream use (grades, reports, emails)

## Core Capabilities

### 1. Context Detection
Automatically identifies artifact type and adjusts approach:
- **Assessment Reports**: Department-level annual reports with SLOs/POs and evidence
- **Student Projects**: Undergraduate assignments, papers, projects, presentations
- **Accreditation Reports**: SACSCOC compliance documents

### 2. Rubric Adaptability
Works with various rubric formats:
- Analytic rubrics (multiple criteria with levels)
- Holistic rubrics (single overall judgment)
- Point-based scales (3-point, 4-point, 5-point, custom)
- Custom descriptors (Exemplary/Proficient/Developing, Meets/Partially Meets/Does Not Meet, etc.)

### 3. Dual-Output Format
Always produces:
1. **Table**: At-a-glance summary with ratings and brief justifications
2. **Narrative**: Detailed feedback organized by strengths and areas for growth

## Evaluation Process

### Step 1: Understand the Context
**Read all provided files:**
- Rubric document
- Artifact to evaluate
- Any reference materials or context documents

**Auto-detect:**
- Artifact type (assessment report, student project, accreditation report)
- Rubric structure (number of criteria, levels, scoring system)
- Evaluation purpose (formative, summative, or both)

**For Assessment Reports, also identify:**
- Whether SLOs or POs are being assessed
- Types of evidence provided (direct vs indirect measures)
- Presence of closing-the-loop elements

**For Accreditation Reports, note:**
- Which SACSCOC standard(s) are being addressed
- Required components for that standard

### Step 2: Apply the Rubric Systematically

#### General Evaluation Principles:
1. **Rate what is demonstrated, not intent**
   - Judge only based on evidence present in the artifact
   - Do not infer or assume missing information
   - Do not fill in gaps based on what "probably" exists

2. **Use preponderance of evidence**
   - Select the level that best matches overall quality for each criterion
   - If evidence splits between two levels, choose the level with stronger/more consistent evidence
   - When truly uncertain between adjacent levels, select the lower level unless clear evidence supports the higher

3. **Document specific evidence**
   - Note page numbers, section references, or specific examples
   - Quote or paraphrase key evidence that informed the rating
   - Identify what's present AND what's missing at higher levels

#### Context-Specific Considerations:

**For Assessment Reports:**
- Check for alignment with best practices:
  - Clear, measurable SLOs/POs
  - Appropriate assessment methods (prefer direct measures)
  - Sufficient sample sizes or participation rates
  - Analysis that moves beyond descriptive statistics
  - Action plans based on findings (closing the loop)
  - Evidence of follow-through from prior cycles
- Note strengths and gaps in the assessment cycle

**For Student Projects:**
- Evaluate against learning objectives and assignment requirements
- Consider developmental appropriateness for undergraduate level
- Identify specific skills/knowledge demonstrated
- Highlight areas showing strong understanding
- Pinpoint concrete opportunities for improvement

**For Accreditation Reports:**
- Cross-reference SACSCOC standard requirements automatically
- Verify all required components are addressed:
  - For 8.2a (Student Outcomes): evidence of systematic assessment of student learning
  - For 9.1 (Program Content): documented evidence of program quality
  - For 9.2 (Program Length): appropriate credit hours and curriculum structure
  - For 10.4 (Research Compliance): IRB and research ethics protocols
  - [Add other standards as referenced in rubric]
- Check for compliance language and required documentation
- Note any missing required elements

### Step 3: Generate Dual-Format Output

#### Output Structure:

```
## EVALUATION SUMMARY

**Artifact**: [Name/Title]
**Artifact Type**: [Assessment Report | Student Project | Accreditation Report]
**Date**: [Current date]
**Evaluator**: [Your name if provided, otherwise "Assessment Team"]

---

## AT-A-GLANCE RATINGS

[Generate table with following structure]

| Criterion | Rating | Brief Justification |
|-----------|--------|---------------------|
| [Criterion 1 name from rubric] | [Level achieved] | [1-2 sentences citing specific evidence] |
| [Criterion 2 name from rubric] | [Level achieved] | [1-2 sentences citing specific evidence] |
| ... | ... | ... |

**Overall Performance**: [If rubric includes overall rating or score]
**Total Points**: [If rubric uses numeric scoring - format for CSV export: "X/Y points"]

---

## DETAILED NARRATIVE FEEDBACK

### Strengths
[Organized by theme or criterion, describe what the artifact does well. Be specific and cite evidence. Length: 2-4 paragraphs depending on artifact complexity]

[For Assessment Reports: Note strong assessment practices, clear alignment, good use of data]
[For Student Projects: Highlight mastery areas, excellent analysis, creativity, strong technical skills]
[For Accreditation Reports: Commend thorough documentation, clear compliance, comprehensive evidence]

### Areas for Growth
[Organized by priority (most important first), describe what needs improvement. Be specific and actionable. Length: 2-4 paragraphs]

[For Assessment Reports: Suggest improvements to methods, analysis depth, closing the loop]
[For Student Projects: Identify learning gaps, suggest study approaches, recommend resources]
[For Accreditation Reports: Note missing required elements, suggest additional documentation]

### Actionable Next Steps
[Provide 3-5 concrete, prioritized recommendations for improvement. Format as a numbered list]

**For Formative Feedback (student-facing or developmental):**
1. [Most critical action - be specific about WHAT to do and HOW]
2. [Second priority - include examples or resources]
3. [Third priority - connect to learning goals]
4-5. [Additional steps if needed]

**For Summative Feedback (grading or compliance):**
- Focus on what would elevate work to next level
- Reference specific rubric criteria
- Maintain professional, objective tone

---

## INTEGRATION DATA

### For Gradebook Export (CSV-ready format):
- Student/Department: [Name]
- Assignment/Report: [Title]
- Total Points: [Numeric score if applicable]
- Criterion 1: [Score]
- Criterion 2: [Score]
- [Continue for all criteria]
- Comments: [One-sentence summary]

### For Email Communication:
[Generate a student-appropriate or chair-appropriate summary that can be inserted into email using rob-email-style or rob-professional-communications skills]

[For Students - warm, encouraging tone]:
"Your [project/paper] demonstrates [key strength]. To strengthen your work further, focus on [priority area]. The detailed feedback above provides specific guidance."

[For Department Chairs - collegial, professional tone]:
"The annual assessment report shows [overall quality level] work in [program]. Key strengths include [X]. To enhance the assessment process, consider [priority recommendation]."

[For Accreditation - formal, compliance-focused tone]:
"The documentation for [Standard X.X] is [compliant/partially compliant/needs revision]. [Brief statement of status]. See detailed feedback for required additions."

### For Assessment Feedback Letters:
[Generate section that can be inserted directly into assessment-feedback-letters skill output]

**[Department/Program Name] - [Academic Year] Assessment Report**

Your assessment report demonstrates [overall characterization]. Particular strengths include:
- [Strength 1 with brief evidence]
- [Strength 2 with brief evidence]

To further strengthen your assessment practices, I recommend:
- [Recommendation 1 - specific and actionable]
- [Recommendation 2 - connected to best practices]

[Additional context about why these recommendations matter for program improvement]
```

## Tone and Style Guidelines

### For Student Projects:
- **Warm and encouraging** while maintaining honesty
- Emphasize growth and learning, not just deficits
- Use second person ("you demonstrated," "your analysis")
- Balance critique with recognition of effort and improvement
- Provide specific examples and resources for improvement
- Frame feedback as developmental, not judgmental

### For Assessment Reports (to Department Chairs):
- **Collegial and professional** (use rob-professional-communications style)
- Assume expertise; focus on refinement, not instruction
- Use inclusive language ("we," "the assessment community")
- Frame suggestions as enhancements, not corrections
- Reference best practices and scholarly literature when relevant
- Acknowledge constraints and context

### For Accreditation Reports:
- **Formal and objective**
- Focus on compliance and documentation sufficiency
- Use precise language about requirements met/unmet
- Maintain neutral, evaluative tone
- Reference specific standard requirements
- Emphasize evidence and documentation quality

## Special Features

### SACSCOC Cross-Reference System
When evaluating accreditation reports, automatically check against standard requirements:

**Standard 8.2a (Student Outcomes)**:
- Required: Assessment plan, data collection, analysis, use of results
- Check for: Clear learning outcomes, direct measures, multi-year evidence

**Standard 9.1 (Program Content)**:
- Required: Currency, quality evidence, learning outcomes alignment
- Check for: Curriculum maps, external review, employer feedback

**Standard 9.2 (Program Length)**:
- Required: Credit hour documentation, justification for length
- Check for: Consistency with peer programs, rationale for structure

**Standard 10.4 (Research Compliance)**:
- Required: IRB protocols, human subjects protection, conflict of interest policies
- Check for: Documentation of processes, training records, oversight

[Add additional standards as they appear in rubrics]

### Assessment Report Best Practices Check
When evaluating assessment reports, automatically verify:

**Assessment Design:**
- [ ] SLOs/POs are specific, measurable, and aligned with program mission
- [ ] Direct measures are prioritized (exams, rubrics, portfolios, capstones)
- [ ] Indirect measures complement (surveys, interviews, focus groups)
- [ ] Sample sizes are sufficient and representative
- [ ] Assessment methods are appropriate for outcomes being measured

**Data Analysis:**
- [ ] Results are disaggregated when appropriate (by section, modality, time)
- [ ] Analysis goes beyond descriptive statistics
- [ ] Trends across multiple cycles are examined
- [ ] Comparison to benchmarks or targets is included
- [ ] Interpretations are supported by evidence

**Closing the Loop:**
- [ ] Findings lead to specific action plans
- [ ] Actions are connected to identified gaps
- [ ] Evidence of implementation from prior cycles
- [ ] Assessment of whether actions improved outcomes
- [ ] Plans for continued improvement are articulated

### CSV Export Format
Structure data for easy gradebook import:

```csv
Student_Name,Assignment,Criterion_1,Criterion_2,Criterion_3,Total_Points,Comments
[Name],[Title],[Score],[Score],[Score],[Total],"[Brief summary]"
```

For assessment reports, adapt to:
```csv
Department,Report_Year,Criterion_1,Criterion_2,Criterion_3,Overall_Rating,Priority_Action
[Dept],[Year],[Rating],[Rating],[Rating],[Overall],"[Top recommendation]"
```

## Integration with Other Skills

This skill is designed to work seamlessly with:

1. **rob-professional-communications**: For drafting emails to department chairs about assessment feedback
2. **rob-email-style**: For crafting student-facing feedback emails
3. **assessment-feedback-letters**: For generating formal annual feedback letters to departments
4. **assessment-newsletter**: For extracting exemplars or common issues to feature in newsletters

When integrating:
- Use the "Integration Data" section outputs
- Maintain consistent tone through cross-skill coordination
- Preserve evaluation data structure for downstream processing

## Error Handling and Edge Cases

**Missing Rubric Information:**
- If rubric levels are unclear, request clarification before evaluating
- If criteria are ambiguous, interpret in most standard way and note assumption

**Incomplete Artifacts:**
- Evaluate only what is present
- Note missing sections in "Areas for Growth"
- Do not penalize for sections not required by assignment/standard

**Non-Applicable Criteria:**
- Mark as "N/A" in table with brief explanation
- Exclude from total score calculations
- Explain why criterion doesn't apply in narrative

**Split Evidence (between two levels):**
- Default to lower level unless strong preponderance supports higher
- Explain the split in justification
- Use narrative to highlight specific examples at each level

**Artifact Demonstrates Skills Not on Rubric:**
- Acknowledge in "Strengths" section
- Do not influence ratings for specified criteria
- Suggest these could inform rubric revision (for assessment reports)

## Quality Checks Before Finalizing

Before providing evaluation to user, verify:
- [ ] Every rubric criterion has been rated
- [ ] Every rating has specific evidence citation
- [ ] Table and narrative are consistent (same ratings, aligned feedback)
- [ ] Tone matches artifact type and audience
- [ ] Actionable next steps are specific and achievable
- [ ] Integration data is properly formatted
- [ ] SACSCOC cross-reference completed (if accreditation report)
- [ ] Best practices check completed (if assessment report)
- [ ] No assumptions made about missing information
- [ ] Evidence sources are cited (page numbers, sections, quotes)

## Examples

### Example 1: Assessment Report Evaluation

**Input**: Department assessment report with rubric for SLO quality, methods, analysis, and use of results

**Output**:
```
## EVALUATION SUMMARY
**Artifact**: Biology Department Annual Assessment Report 2024-25
**Artifact Type**: Assessment Report
**Date**: November 2, 2025

---

## AT-A-GLANCE RATINGS

| Criterion | Rating | Brief Justification |
|-----------|--------|---------------------|
| SLO Quality | Proficient | SLOs are measurable and aligned with program outcomes (p. 2). All five SLOs use action verbs and specify criteria, though some could be more specific about proficiency levels. |
| Assessment Methods | Developing | Uses capstone rubric (direct) and exit survey (indirect), but relies heavily on indirect measures for SLOs 3-5 (pp. 4-6). Sample sizes for direct measures are small (n=12 capstones). |
| Data Analysis | Proficient | Clear presentation of results with disaggregation by track (p. 8). Three-year trends shown. Analysis identifies patterns but could deepen interpretation of why results differ across tracks. |
| Use of Results | Exemplary | Strong closing-the-loop evidence. Action plan from 2023 (revise lab sequence) was implemented and improvements documented (pp. 10-11). New action plan is specific and timeline-driven (p. 12). |

**Overall Performance**: Proficient

---

## DETAILED NARRATIVE FEEDBACK

### Strengths
The Biology Department demonstrates several hallmarks of mature assessment practice. Most notably, the report provides exemplary evidence of closing the loop (Use of Results criterion). The narrative clearly traces how findings from the 2022-23 cycle led to specific curricular revisions in the lab sequence, describes the implementation process, and presents evidence that these changes resulted in improved student performance on lab-based assessments (pp. 10-11). This represents sophisticated use of assessment data to drive meaningful program improvement.

The SLO quality is strong, with all five outcomes using measurable action verbs and aligning well with the program's stated learning goals. The data analysis section effectively uses visual displays and disaggregates results by track (traditional vs. health professions), revealing important differences in student performance that warrant further investigation.

### Areas for Growth
The primary area for development concerns the balance and robustness of assessment methods. While the capstone project provides excellent direct evidence for SLOs 1-2, the department relies primarily on indirect measures (exit surveys and employer questionnaires) for SLOs 3-5 (pp. 4-6). This creates gaps in understanding what students can actually *do* versus what they *perceive* they can do. Additionally, the sample size for the capstone assessment (n=12) represents only about 30% of graduating seniors, raising questions about representativeness.

The data analysis, while clearly presented, would benefit from deeper interpretation. For example, the finding that health professions track students significantly outperform traditional track students on SLO 2 (quantitative reasoning) is noted (p. 8) but not explored. What might account for this difference? Do these tracks have different prerequisite requirements, advising patterns, or course-taking behaviors?

### Actionable Next Steps
1. **Expand direct assessment methods**: Develop embedded assessments in required upper-level courses to directly measure SLOs 3-5. For instance, SLO 3 (information literacy) could be assessed through a standardized literature review assignment in BIOL 450.

2. **Increase capstone participation**: Either require all seniors to complete the capstone for graduation, or develop an alternative assessment mechanism for the ~70% who don't. Consider whether these students differ systematically from capstone completers.

3. **Deepen data interpretation**: In the next cycle, include a section that explores possible explanations for track differences and other patterns. This might involve pulling additional data (course-taking patterns, GPA, demographic factors) or gathering qualitative data through focus groups.

4. **Specify proficiency targets**: For the next revision of SLOs, add specific proficiency expectations (e.g., "Students will demonstrate quantitative reasoning by correctly applying at least 3 statistical methods to biological data with 80% accuracy").

---

## INTEGRATION DATA

### For Assessment Feedback Letters:
**Biology Department - 2024-25 Annual Assessment Report**

Your assessment report demonstrates proficient assessment practice with exemplary closing-the-loop processes. Particular strengths include:
- Outstanding documentation of how prior findings led to curriculum revision and evidence of resulting improvements
- Well-constructed, measurable SLOs that align with program goals
- Clear presentation of multi-year trends with appropriate disaggregation

To further strengthen your assessment practices, I recommend:
- Expanding direct assessment methods to cover all five SLOs, particularly 3-5 which currently rely on indirect measures
- Increasing participation in capstone assessment or developing alternative mechanisms to ensure representative sampling
- Deepening interpretation of findings, especially notable patterns like track differences in quantitative reasoning performance

These enhancements would provide even richer data to guide program decisions and strengthen the evidence base for continuous improvement. Your current trajectory demonstrates strong commitment to assessment and data-informed decision-making.
```

### Example 2: Student Project Evaluation

**Input**: Undergraduate research paper with rubric for thesis, evidence, analysis, organization, and mechanics

**Output**:
```
## EVALUATION SUMMARY
**Artifact**: "The Impact of Social Media on Adolescent Self-Esteem: A Literature Review"
**Artifact Type**: Student Project (Undergraduate)
**Date**: November 2, 2025

---

## AT-A-GLANCE RATINGS

| Criterion | Rating | Brief Justification |
|-----------|--------|---------------------|
| Thesis & Argument | Proficient | Clear, arguable thesis stating that social media has predominantly negative effects on adolescent self-esteem (p. 1). Thesis is maintained throughout, though some nuance about positive effects could strengthen argument. |
| Use of Evidence | Developing | Uses 8 peer-reviewed sources appropriately cited. However, sources are mostly from 2015-2018; missing more recent research. Some key claims lack sufficient support (e.g., assertion about Instagram on p. 4). |
| Analysis & Critical Thinking | Proficient | Effectively synthesizes multiple sources to identify common themes. Shows good understanding of correlation vs. causation issues (p. 5). Could push analysis further by examining methodological limitations of cited studies. |
| Organization & Structure | Exemplary | Excellent logical flow with clear topic sentences. Smooth transitions between paragraphs. Introduction effectively sets up argument and conclusion ties everything together well. Subheadings help guide reader. |
| Mechanics & Style | Proficient | Generally strong writing with few grammatical errors. APA formatting is correct for citations and references. Some sentences are wordy and could be more concise (especially in introduction). |

**Overall Performance**: Proficient
**Total Points**: 42/50 points

---

## DETAILED NARRATIVE FEEDBACK

### Strengths
Your paper demonstrates strong organizational skills and a clear understanding of the relationship between social media use and adolescent self-esteem. The structure is excellent—you use topic sentences effectively to guide your reader, and your transitions between ideas are smooth and logical. The subheadings ("Types of Social Media Effects," "Gender Differences," "Developmental Considerations") help organize complex information in a reader-friendly way.

Your thesis is clear and well-positioned, and you maintain focus on it throughout the paper. I particularly appreciated your discussion of correlation versus causation on page 5, where you acknowledge that while research shows relationships between social media use and self-esteem, we can't definitively say social media *causes* these effects. This shows sophisticated critical thinking.

Your writing mechanics are generally strong, with proper APA formatting for both in-text citations and your reference list. You clearly understand how to integrate sources into your own writing and give appropriate credit.

### Areas for Growth
The most significant area for improvement is the currency and depth of your evidence. While you use 8 sources effectively, most are from 2015-2018. Given how rapidly social media platforms evolve (TikTok, for instance, didn't exist in 2015), more recent research would strengthen your argument considerably. The field has produced substantial new research in 2022-2024 that examines newer platforms and more recent usage patterns.

Additionally, some of your key claims would benefit from more support. For example, on page 4, you state that "Instagram is particularly harmful to teenage girls' body image," but you cite only one study. Given the importance of this claim to your overall argument, supporting it with 2-3 studies would make it more convincing.

Your analysis is solid, but you could push it further by examining the quality of the research you cite. For instance, what sample sizes did these studies use? Were they longitudinal or cross-sectional? What are the limitations of survey-based research on this topic? Adding this layer of methodological critique would elevate your analysis from "proficient" to "exemplary."

Finally, while your writing is generally clear, some sentences get a bit wordy. For example, in your introduction: "In today's modern contemporary society in which we live, adolescents are faced with the reality of social media being a pervasive and omnipresent force" could be simplified to "Social media is a pervasive force in adolescents' lives today."

### Actionable Next Steps
1. **Update your literature search**: Use PsycINFO or Google Scholar to find 3-5 articles published in 2022-2024 on social media and adolescent self-esteem. Look particularly for research on TikTok and Instagram Reels, which represent newer forms of social media. The search terms "social media AND adolescent self-esteem AND 2024" should help.

2. **Add methodological critique**: Choose 2-3 of your key cited studies and add a sentence or two analyzing their methodology. Ask yourself: How large was the sample? Was it diverse? What were the limitations? This shows deeper engagement with the research.

3. **Strengthen evidence for major claims**: Find at least one additional source to support your claim about Instagram and body image. Look for meta-analyses or systematic reviews that synthesize findings across multiple studies.

4. **Revise for conciseness**: Read through your introduction and look for redundant phrases or strings of similar adjectives. Try reading sentences aloud—if you run out of breath, they're probably too long!

5. **Consider counterarguments**: While your thesis argues for predominantly negative effects, briefly acknowledging research that shows positive effects of social media (online support communities, for instance) and then explaining why you find the negative evidence more compelling would strengthen your argument.

---

## INTEGRATION DATA

### For Gradebook Export:
Student_Name,Assignment,Thesis_Argument,Use_Evidence,Analysis_Thinking,Organization,Mechanics,Total_Points,Comments
[Student Name],Literature Review,9/10,7/10,9/10,10/10,7/10,42/50,"Strong organization and thesis; update sources and add methodological critique"

### For Email Communication:
Your literature review demonstrates strong organizational skills and a clear, well-developed thesis. The structure and flow of your paper are excellent, and you show good critical thinking about correlation versus causation. To strengthen your work for the revision, focus on updating your sources to include more recent research (2022-2024) and adding methodological critique of the studies you cite. The detailed feedback above provides specific guidance on these areas. You're on the right track—these revisions will elevate an already solid paper!
```

## Final Notes

- Always read the entire artifact before beginning evaluation
- Never rate based on assumed intent; only evaluate demonstrated work
- Maintain appropriate tone for audience (student-facing vs. professional)
- Provide integration-ready outputs for seamless workflow
- When in doubt about a rating, choose the lower level and explain ambiguity
- Quality feedback is specific, evidence-based, and actionable
