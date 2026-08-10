const config = window.PYCHRONICLE;

const events = config.events || [];

const watchVariables =
    config.watchVariables || [];

const watchHistory =
    config.watchHistory || [];

let currentStep =
    Math.max(
        0,
        config.totalSteps - 1
    );


const slider =
    document.getElementById(
        "timeline-slider"
    );

const stepNumber =
    document.getElementById(
        "step-number"
    );

const sliderStep =
    document.getElementById(
        "slider-step"
    );

const currentLine =
    document.getElementById(
        "current-line"
    );

const variablesContainer =
    document.getElementById(
        "variables"
    );

const timelineContainer =
    document.getElementById(
        "timeline-list"
    );

const watchContainer =
    document.getElementById(
        "watch-values"
    );

const watchHistoryContainer =
    document.getElementById(
        "watch-history-table"
    );


function escapeHtml(value) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        String(value);

    return div.innerHTML;
}


function updateCodeHighlight(
    lineNumber
) {

    const lines =
        document.querySelectorAll(
            ".code-line"
        );

    lines.forEach(
        (line) => {

            const lineValue =
                Number(
                    line.dataset.line
                );

            line.classList.toggle(
                "active",
                lineValue === lineNumber
            );

        }
    );
}


function renderTimeline() {

    timelineContainer.innerHTML =
        "";

    if (!events.length) {

        timelineContainer.innerHTML =
            `
            <div class="empty-state">
                No execution events found.
            </div>
            `;

        return;
    }


    const start =
        Math.max(
            0,
            currentStep - 8
        );

    const end =
        Math.min(
            events.length,
            currentStep + 9
        );


    for (
        let index = start;
        index < end;
        index++
    ) {

        const event =
            events[index];

        const item =
            document.createElement(
                "div"
            );

        item.className =
            "timeline-item";

        if (
            index === currentStep
        ) {

            item.classList.add(
                "active"
            );

        }


        const changed =
            event.changed.length
                ? event.changed.join(
                    ", "
                )
                : "no variable change";


        let deleted = "";

        if (
            event.deleted.length
        ) {

            deleted =
                " · deleted: "
                + event.deleted.join(
                    ", "
                );

        }


        item.innerHTML =
            `
            <div class="timeline-step">
                Step ${index + 1}
                · Line ${event.line}
            </div>

            <div class="timeline-line">
                ${escapeHtml(
                    event.source
                )}
            </div>

            <div class="timeline-change">
                ${escapeHtml(
                    changed + deleted
                )}
            </div>
            `;


        item.addEventListener(
            "click",
            () => {

                loadStep(index);

            }
        );


        timelineContainer.appendChild(
            item
        );

    }

}


function renderVariables(
    state
) {

    variablesContainer.innerHTML =
        "";

    const names =
        Object.keys(state)
            .sort();


    if (!names.length) {

        variablesContainer.innerHTML =
            `
            <div class="empty-state">
                No reconstructed variables.
            </div>
            `;

        return;
    }


    names.forEach(
        (name) => {

            const row =
                document.createElement(
                    "div"
                );

            row.className =
                "variable-row";


            row.innerHTML =
                `
                <span class="variable-name">
                    ${escapeHtml(name)}
                </span>

                <span class="variable-value">
                    ${escapeHtml(
                        state[name]
                    )}
                </span>
                `;


            variablesContainer.appendChild(
                row
            );

        }
    );

}


function renderWatch(
    state
) {

    if (!watchContainer) {
        return;
    }


    watchContainer.innerHTML =
        "";


    if (!watchVariables.length) {

        return;

    }


    watchVariables.forEach(
        (name) => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "watch-value-card";


            const value =
                Object.prototype.hasOwnProperty
                    .call(state, name)
                    ? state[name]
                    : "<not defined>";


            card.innerHTML =
                `
                <div class="watch-name">
                    ${escapeHtml(name)}
                </div>

                <div class="watch-value">
                    ${escapeHtml(value)}
                </div>
                `;


            watchContainer.appendChild(
                card
            );

        }
    );

}


function renderWatchHistory() {

    if (
        !watchHistoryContainer
    ) {

        return;

    }


    watchHistoryContainer.innerHTML =
        "";


    if (!watchVariables.length) {
        return;
    }


    const start =
        Math.max(
            0,
            currentStep - 8
        );


    const end =
        Math.min(
            watchHistory.length,
            currentStep + 1
        );


    for (
        let index = start;
        index < end;
        index++
    ) {

        const entry =
            watchHistory[index];


        const row =
            document.createElement(
                "div"
            );

        row.className =
            "watch-history-row";


        const values =
            watchVariables
                .map(
                    (name) => {

                        const value =
                            entry.values[
                                name
                            ] ??
                            "<not defined>";

                        return (
                            `${name}=${value}`
                        );

                    }
                )
                .join(
                    " · "
                );


        row.innerHTML =
            `
            <span>
                Step ${index + 1}
            </span>

            <span>
                ${escapeHtml(values)}
            </span>
            `;


        watchHistoryContainer.appendChild(
            row
        );

    }

}


async function loadStep(
    step
) {

    if (!events.length) {
        return;
    }


    currentStep =
        Math.max(
            0,
            Math.min(
                step,
                events.length - 1
            )
        );


    try {

        const response =
            await fetch(
                `/api/runs/${encodeURIComponent(
                    config.runId
                )}/step/${currentStep}`
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load execution state."
            );

        }


        const data =
            await response.json();


        slider.value =
            currentStep;


        stepNumber.textContent =
            currentStep + 1;


        sliderStep.textContent =
            `Step ${currentStep + 1}`;


        currentLine.textContent =
            `Line ${data.line_number}`;


        updateCodeHighlight(
            data.line_number
        );


        renderVariables(
            data.state
        );


        renderWatch(
            data.state
        );


        renderWatchHistory();

        renderTimeline();

    } catch (error) {

        console.error(
            error
        );

    }

}


/* ---------------------------------------
   BUTTONS
--------------------------------------- */

document
    .getElementById(
        "first-button"
    )
    .addEventListener(
        "click",
        () => loadStep(0)
    );


document
    .getElementById(
        "previous-button"
    )
    .addEventListener(
        "click",
        () => loadStep(
            currentStep - 1
        )
    );


document
    .getElementById(
        "next-button"
    )
    .addEventListener(
        "click",
        () => loadStep(
            currentStep + 1
        )
    );


document
    .getElementById(
        "last-button"
    )
    .addEventListener(
        "click",
        () => loadStep(
            events.length - 1
        )
    );


/* ---------------------------------------
   RANGE SLIDER
--------------------------------------- */

slider.addEventListener(
    "input",
    (event) => {

        loadStep(
            Number(
                event.target.value
            )
        );

    }
);


/* ---------------------------------------
   KEYBOARD NAVIGATION
--------------------------------------- */

document.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "ArrowLeft"
        ) {

            loadStep(
                currentStep - 1
            );

        }


        if (
            event.key === "ArrowRight"
        ) {

            loadStep(
                currentStep + 1
            );

        }


        if (
            event.key === "Home"
        ) {

            loadStep(0);

        }


        if (
            event.key === "End"
        ) {

            loadStep(
                events.length - 1
            );

        }

    }
);


/* ---------------------------------------
   INITIAL STATE
--------------------------------------- */

loadStep(
    currentStep
);