from __future__ import annotations

from homunculus.role_ref import RoleRef

DEFAULT_INCLUDE_ROLES = {"button", "textbox", "link", "checkbox", "radio", "combobox"}


def snapshot_role_refs(
    page, include_roles: set[str] | None = None, visible_only: bool = True
) -> list[str]:
    roles = include_roles or DEFAULT_INCLUDE_ROLES
    role_refs: list[str] = []
    counters: dict[tuple[str, str], int] = {}

    name_script = """
(el) => {
  const normalize = (text) => {
    if (!text) {
      return "";
    }
    return text.replace(/\\s+/g, " ").trim();
  };

  const attrValue = (attrName) => {
    const value = el.getAttribute(attrName);
    return value ? normalize(value) : "";
  };

  let name = attrValue("aria-label");
  if (!name) {
    const labelledby = el.getAttribute("aria-labelledby");
    if (labelledby) {
      const ids = labelledby.split(/\\s+/).filter(Boolean);
      const parts = ids.map((id) => {
        const node = el.ownerDocument.getElementById(id);
        if (!node) {
          return "";
        }
        return normalize(node.innerText || node.textContent || "");
      });
      name = normalize(parts.filter(Boolean).join(" "));
    }
  }
  if (!name && el.labels && el.labels.length) {
    const parts = Array.from(el.labels).map((label) =>
      normalize(label.innerText || label.textContent || "")
    );
    name = normalize(parts.filter(Boolean).join(" "));
  }
  if (!name) {
    name = attrValue("alt");
  }
  if (!name) {
    name = attrValue("title");
  }
  if (!name) {
    name = normalize(el.innerText || el.textContent || "");
  }
  return name;
}
"""

    for role in sorted(roles):
        locator = page.get_by_role(role, include_hidden=True)
        try:
            count = locator.count()
        except Exception:
            continue
        for index in range(count):
            element = locator.nth(index)
            if visible_only:
                try:
                    if not element.is_visible():
                        continue
                except Exception:
                    pass
            try:
                name = element.evaluate(name_script)
            except Exception:
                continue
            if not name:
                continue
            key = (role, name)
            nth = counters.get(key, 0)
            counters[key] = nth + 1
            role_refs.append(RoleRef(role=role, name=name, nth=nth).to_str())

    return role_refs
