#!/usr/bin/env python3
"""Compilador oficial de edições da newsletter 'Decifrando Dados' (Modelo Oficial em Duas Etapas).

Salva por padrão TODAS as gerações (.html, .pdf, _artigo_linkedin.txt e .md) em:
C:\\Users\\marlo\\OneDrive\\Desktop\\Pasta Projetos\\01_Newsletter_Decifrando_Dados\\edicoes
"""

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

OFFICIAL_EDICOES_DIR = Path(
    r"C:\Users\marlo\OneDrive\Desktop\Pasta Projetos\01_Newsletter_Decifrando_Dados\edicoes"
)

DIAS_SEMANA_PT = {
    0: "SEGUNDA-FEIRA",
    1: "TERÇA-FEIRA",
    2: "QUARTA-FEIRA",
    3: "QUINTA-FEIRA",
    4: "SEXTA-FEIRA",
    5: "SÁBADO",
    6: "DOMINGO",
}

MESES_PT = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO",
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO",
}


def format_date_pt(date_str: str) -> str:
    """Converte DD/MM/AAAA para 'TERÇA-FEIRA, 13 DE OUTUBRO'."""
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        dia_sem = DIAS_SEMANA_PT.get(dt.weekday(), "HOJE")
        mes = MESES_PT.get(dt.month, "OUTUBRO")
        return f"{dia_sem}, {dt.day} DE {mes}"
    except Exception:
        now = datetime.now()
        return f"{DIAS_SEMANA_PT[now.weekday()]}, {now.day} DE {MESES_PT[now.month]}"


def format_inline(text: str) -> str:
    """Formata negrito, itálico, código e 'Leia mais →' inline para HTML."""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = text.replace(
        "Leia mais →",
        "<span class='read-more-tag'>Leia mais &rarr;</span>",
    )
    return text


def parse_markdown_to_html(md_text: str) -> tuple[dict, str, str, str]:
    """Extrai metadados, corpo HTML visual Decifrando Dados, HTML limpo para LinkedIn e texto pacote."""
    now_str = datetime.now().strftime("%d/%m/%Y")
    metadata = {
        "titulo": "O ABACAXI BILIONÁRIO DOS DADOS E DA IA",
        "subtitulo": "Smart people are cooler — Dados reais mastigados e zero corporatiquês",
        "assunto": "",
        "categoria": "NEGÓCIOS & IA",
        "edicao": "01",
        "data": now_str,
        "dia_semana": "",
        "tempo_leitura": "4",
    }

    lines = md_text.splitlines()
    body_lines = []
    in_frontmatter = False
    current_key = None
    multiline_buf = []

    for i, line in enumerate(lines):
        striped = line.strip()
        if i == 0 and striped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if striped == "---":
                if current_key and multiline_buf:
                    metadata[current_key] = "\n".join(multiline_buf).strip()
                in_frontmatter = False
                continue
            if re.match(r"^[a-zA-Z0-9_\-]+:", line):
                if current_key and multiline_buf:
                    metadata[current_key] = "\n".join(multiline_buf).strip()
                    multiline_buf = []
                k, v = line.split(":", 1)
                current_key = k.strip().lower()
                val = v.strip().strip('"').strip("'")
                if val in ("|", ">", ""):
                    multiline_buf = []
                else:
                    metadata[current_key] = val
                    current_key = None
            elif current_key is not None:
                multiline_buf.append(line.strip())
            continue
        body_lines.append(line)

    if not metadata.get("dia_semana"):
        metadata["dia_semana"] = format_date_pt(metadata.get("data", now_str))

    body_md = "\n".join(body_lines).strip()

    m_h1 = re.search(r"^#\s+(.+)$", body_md, re.MULTILINE)
    if m_h1 and metadata.get("titulo") == "O ABACAXI BILIONÁRIO DOS DADOS E DA IA":
        metadata["titulo"] = m_h1.group(1).strip()

    if not metadata.get("assunto"):
        short_subj = metadata.get("titulo", "EDIÇÃO DA SEMANA")[:34].upper()
        metadata["assunto"] = f"⚡ {short_subj}"

    html_out = []
    linkedin_html = [
        f"<p>📬 <strong>De:</strong> Decifrando Dados • Marlon Ferreira &nbsp;|&nbsp; 📅 <strong>Edição #{metadata.get('edicao', '01')}</strong> &nbsp;|&nbsp; <em>Smart people are cooler.</em></p>"
    ]

    section_mode = None
    section_items = []
    pending_pill_title = None
    tradutor_data = {"termo": "", "itens": []}
    parceria_lines = []
    in_parceria = False
    main_headline_rendered = False

    def flush_section():
        nonlocal section_mode, section_items, pending_pill_title, tradutor_data
        if not section_mode:
            return
        if section_mode == "indice" and section_items:
            li_html = "".join(f"<li>{item}</li>" for item in section_items)
            box_title = "📌 NESTA EDIÇÃO" if any("NESTA EDIÇÃO" in str(x).upper() for x in section_items) else "⚡ O QUE VOCÊ VAI VER HOJE?"
            html_out.append(
                f"<div class='indice-box'>"
                f"<div class='indice-title'>{box_title}</div>"
                f"<ul class='indice-grid'>{li_html}</ul>"
                f"</div>"
            )
            linkedin_html.append(f"<h3>{box_title}</h3>")
            linkedin_html.append(f"<ul>{li_html}</ul>")
        elif section_mode == "radar" and section_items:
            cards = "".join(f"<div class='radar-item'>{item}</div>" for item in section_items)
            html_out.append(f"<div class='radar-grid'>{cards}</div>")
            li_html = "".join(f"<li>{item}</li>" for item in section_items)
            linkedin_html.append(f"<ul>{li_html}</ul>")
        elif section_mode == "tradutor":
            if tradutor_data.get("termo") or tradutor_data.get("itens"):
                termo = tradutor_data.get("termo", "Conceito Técnico da Semana")
                rows = "".join(f"<div class='tradutor-row'>{it}</div>" for it in tradutor_data.get("itens", []))
                html_out.append(
                    f"<div class='tradutor-box'>"
                    f"<div class='tradutor-kicker'>📖 TRADUTOR DE IA & DADOS (1 TERMO POR EDIÇÃO)</div>"
                    f"<div class='tradutor-termo'>{termo}</div>"
                    f"{rows}"
                    f"</div>"
                )
                linkedin_html.append(f"<h3>📖 Tradutor de IA & Dados — {termo}</h3>")
                linkedin_html.append(f"<ul>{''.join(f'<li>{it}</li>' for it in tradutor_data.get('itens', []))}</ul>")
            tradutor_data = {"termo": "", "itens": []}
        elif section_mode == "resumao" and section_items:
            li_html = "".join(f"<li>{item}</li>" for item in section_items)
            html_out.append(
                f"<div class='resumao-box'>"
                f"<div class='resumao-title'>🗞️ RESUMÃO RÁPIDO DA SEMANA</div>"
                f"<ul>{li_html}</ul>"
                f"</div>"
            )
            linkedin_html.append("<h3>🗞️ RESUMÃO RÁPIDO DA SEMANA</h3>")
            linkedin_html.append(f"<ul>{li_html}</ul>")
        elif section_mode == "recomenda" and section_items:
            rec_cards = []
            rec_li = []
            for item in section_items:
                if ":" in item:
                    t_part, d_part = item.split(":", 1)
                    t_clean = re.sub(r"</?strong>", "", t_part).strip()
                    rec_cards.append(
                        f"<div class='recomenda-card'>"
                        f"<div class='recomenda-kicker'>✍️ A REDAÇÃO RECOMENDA</div>"
                        f"<div class='recomenda-title'>{t_clean}</div>"
                        f"<div class='recomenda-desc'>{d_part.strip()}</div>"
                        f"</div>"
                    )
                else:
                    rec_cards.append(
                        f"<div class='recomenda-card'>"
                        f"<div class='recomenda-kicker'>✍️ A REDAÇÃO RECOMENDA</div>"
                        f"<div class='recomenda-desc'>{item}</div>"
                        f"</div>"
                    )
                rec_li.append(f"<li>{item}</li>")
            html_out.append(f"<div class='recomenda-grid'>{''.join(rec_cards)}</div>")
            linkedin_html.append("<h3>✍️ A REDAÇÃO RECOMENDA</h3>")
            linkedin_html.append(f"<ul>{''.join(rec_li)}</ul>")
        section_mode = None
        section_items = []
        pending_pill_title = None

    def flush_parceria():
        nonlocal in_parceria, parceria_lines
        if not in_parceria or not parceria_lines:
            in_parceria = False
            parceria_lines = []
            return
        header_line = parceria_lines[0]
        body_part = " ".join(parceria_lines[1:]) if len(parceria_lines) > 1 else ""
        header_clean = re.sub(r"</?strong>", "", format_inline(header_line))
        body_formatted = format_inline(body_part)
        html_out.append(
            f"<div class='parceria-box'>"
            f"<div class='parceria-header'>{header_clean}</div>"
            f"<p style='margin:0;'>{body_formatted}</p>"
            f"</div>"
        )
        linkedin_html.append(
            f"<blockquote><strong>{header_clean}</strong><br>{body_formatted}</blockquote>"
        )
        in_parceria = False
        parceria_lines = []

    for raw_line in body_lines:
        line = raw_line.strip()

        if not line:
            if in_parceria:
                flush_parceria()
            continue

        if re.match(r"^---+$", line):
            flush_parceria()
            flush_section()
            continue

        if in_parceria:
            if line.startswith(">"):
                parceria_lines.append(line.lstrip(">").strip())
                continue
            else:
                flush_parceria()

        # 1. Fato Histórico (Efeméride no topo)
        if (
            (line.startswith(">") and ("Há " in line or "🕰️" in line))
            or re.match(r"^(🕰️\s*)?\**Há\s+\d+\s+anos", line, re.IGNORECASE)
        ):
            flush_section()
            clean_hist = line.lstrip(">").strip()
            clean_hist = re.sub(r"^🕰️\s*", "", clean_hist)
            formatted_hist = format_inline(clean_hist)
            html_out.append(f"<div class='fato-historico-box'>{formatted_hist}</div>")
            linkedin_html.append(f"<blockquote>🕰️ {formatted_hist}</blockquote>")
            continue

        # 2. Detectar Cabeçalhos de Seções Especiais (Newsletter & LinkedIn Guia)
        upper_line = line.upper()
        is_bullet_line = bool(re.match(r"^[\*\-]\s+", line))

        if not is_bullet_line and ("O QUE VOCÊ VAI VER HOJE" in upper_line or "NESTA EDIÇÃO" in upper_line):
            flush_section()
            section_mode = "indice"
            continue

        if not is_bullet_line and ("TRADUTOR DE IA" in upper_line or "TRADUTOR DA SEMANA" in upper_line):
            flush_section()
            section_mode = "tradutor"
            tradutor_data = {"termo": "", "itens": []}
            continue

        if not is_bullet_line and ("RADAR RÁPIDO" in upper_line or "RADAR DA SEMANA" in upper_line or "DE OLHO NO" in upper_line):
            flush_section()
            section_mode = "radar"
            kicker = "RADAR DO ECOSSISTEMA" if "DE OLHO NO" in upper_line else "RADAR DA SEMANA"
            header_title = "👀 DE OLHO NO ECOSSISTEMA <span class='sub-note'>(o grande irmão)</span>" if "DE OLHO NO" in upper_line else "⚡ RADAR RÁPIDO DA SEMANA"
            html_out.append(f"<div class='section-kicker'>{kicker}</div>")
            html_out.append(f"<div class='section-header-title'>{header_title}</div>")
            linkedin_html.append(f"<h2>{header_title}</h2>")
            continue

        if not is_bullet_line and ("DON'T LEAVE, JUST READ" in upper_line or "DONT LEAVE, JUST READ" in upper_line):
            flush_section()
            section_mode = "dont_leave"
            html_out.append("<div class='section-kicker green'>PÍLULAS RELÂMPAGO</div>")
            html_out.append(
                "<div class='section-header-title'>🏃‍♀️ DON'T LEAVE, JUST READ <span class='sub-note'>(pra ler no segundo café)</span></div>"
            )
            linkedin_html.append("<h2>🏃‍♀️ DON'T LEAVE, JUST READ (pra ler no segundo café)</h2>")
            continue

        if not is_bullet_line and "RESUMÃO" in upper_line:
            flush_section()
            section_mode = "resumao"
            continue

        if not is_bullet_line and "A REDAÇÃO RECOMENDA" in upper_line:
            flush_section()
            section_mode = "recomenda"
            continue

        # Detectar termo da vez dentro do bloco Tradutor
        if section_mode == "tradutor" and "O TERMO DA VEZ" in upper_line:
            t_val = line.split(":", 1)[1].strip().strip("*").strip()
            tradutor_data["termo"] = format_inline(t_val)
            continue

        # Detectar Assinatura ou Gostou desta edição
        if ("GOSTOU DESTA EDIÇÃO" in upper_line or line.startswith("Assinatura:")) and not is_bullet_line:
            flush_section()
            clean_ass = re.sub(r"^\**Assinatura:\**\s*", "", line, flags=re.IGNORECASE)
            formatted_ass = format_inline(clean_ass)
            html_out.append(f"<div class='assinatura-box'>{formatted_ass}</div>")
            linkedin_html.append(f"<hr><p>{formatted_ass}</p>")
            continue

        m_list = re.match(r"^[\*\-]\s+(.+)$", line)
        if m_list:
            raw_item = m_list.group(1).strip()
            item_content = format_inline(raw_item)
            upper_raw = raw_item.upper()

            if section_mode == "tradutor":
                tradutor_data["itens"].append(item_content)
                continue

            # As 3 Lentes Práticas (TI, Bancos, Negócios)
            if any(k in upper_raw for k in ("PARA TECNOLOGIA E DADOS", "PARA TECNOLOGIA", "EM TI E DADOS", "EM TI:")):
                clean_desc = re.sub(r"^\**Para (?:Tecnologia e Dados \(TI\)|Tecnologia|TI(?:\s+e\s+Dados)?):\**\s*", "", raw_item, flags=re.IGNORECASE)
                desc_fmt = format_inline(clean_desc)
                html_out.append(
                    f"<div class='lente-card ti'>"
                    f"<div class='lente-header'>💻 Para Tecnologia e Dados (TI)</div>"
                    f"<p style='margin:0;'>{desc_fmt}</p>"
                    f"</div>"
                )
                linkedin_html.append(f"<p>• <strong>Para Tecnologia e Dados (TI):</strong> {desc_fmt}</p>")
                continue

            if any(k in upper_raw for k in ("PARA O SETOR BANCÁRIO", "PARA O SETOR FINANCEIRO", "EM BANCOS E FINANÇAS", "EM BANCOS:")):
                clean_desc = re.sub(r"^\**Para o (?:Setor Bancário e Financeiro|Setor Bancário|Setor Financeiro|Bancos):\**\s*", "", raw_item, flags=re.IGNORECASE)
                desc_fmt = format_inline(clean_desc)
                html_out.append(
                    f"<div class='lente-card bancos'>"
                    f"<div class='lente-header'>🏦 Para o Setor Bancário e Financeiro</div>"
                    f"<p style='margin:0;'>{desc_fmt}</p>"
                    f"</div>"
                )
                linkedin_html.append(f"<p>• <strong>Para o Setor Bancário e Financeiro:</strong> {desc_fmt}</p>")
                continue

            if any(k in upper_raw for k in ("PARA NEGÓCIOS E PÚBLICO GERAL", "PARA NEGÓCIOS", "NOS NEGÓCIOS E DIA A DIA", "NOS NEGÓCIOS:")):
                clean_desc = re.sub(r"^\**Para (?:Negócios e Público Geral|Negócios|Público Geral):\**\s*", "", raw_item, flags=re.IGNORECASE)
                desc_fmt = format_inline(clean_desc)
                html_out.append(
                    f"<div class='lente-card negocios'>"
                    f"<div class='lente-header'>📊 Para Negócios e Público Geral</div>"
                    f"<p style='margin:0;'>{desc_fmt}</p>"
                    f"</div>"
                )
                linkedin_html.append(f"<p>• <strong>Para Negócios e Público Geral:</strong> {desc_fmt}</p>")
                continue

            if section_mode in ("indice", "radar", "resumao", "recomenda"):
                section_items.append(item_content)
                continue
            elif section_mode == "dont_leave":
                html_out.append(f"<div class='pill-card'><p>{item_content}</p></div>")
                linkedin_html.append(f"<p>• {item_content}</p>")
                continue
            else:
                html_out.append(f"<ul><li>{item_content}</li></ul>")
                linkedin_html.append(f"<ul><li>{item_content}</li></ul>")
                continue

        if section_mode == "dont_leave":
            if line.startswith("#"):
                pending_pill_title = format_inline(line.lstrip("#").strip())
                continue
            elif pending_pill_title:
                p_body = format_inline(line)
                html_out.append(
                    f"<div class='pill-card'>"
                    f"<div class='pill-title'>{pending_pill_title}</div>"
                    f"<p>{p_body}</p>"
                    f"</div>"
                )
                linkedin_html.append(f"<h3>{pending_pill_title}</h3><p>{p_body}</p>")
                pending_pill_title = None
                continue

        if section_mode in ("indice", "radar", "resumao", "recomenda", "tradutor"):
            flush_section()

        # 3. Painel de 3 Métricas
        if line.startswith("|") and line.endswith("|") and line.count("|") >= 4:
            cells = [c.strip() for c in line.strip("|").split("|") if c.strip()]
            if not all(re.match(r"^[\-:]+$", c) for c in cells):
                card_divs = []
                li_metrics = []
                for cell in cells:
                    m_bold = re.search(r"\*\*(.+?)\*\*", cell)
                    if m_bold:
                        val = html.escape(m_bold.group(1))
                        desc = cell.replace(m_bold.group(0), "").strip(" —-–:")
                        desc_html = format_inline(desc)
                    elif "—" in cell:
                        v_p, d_p = cell.split("—", 1)
                        val = html.escape(v_p.strip())
                        desc_html = format_inline(d_p.strip())
                    else:
                        val = format_inline(cell)
                        desc_html = ""
                    card_divs.append(
                        f"<div class='metric-card'>"
                        f"<div class='metric-val'>{val}</div>"
                        f"<div class='metric-desc'>{desc_html}</div>"
                        f"</div>"
                    )
                    li_metrics.append(f"<li><strong>{val}:</strong> {desc_html}</li>")
                html_out.append(f"<div class='metrics-grid'>{''.join(card_divs)}</div>")
                linkedin_html.append(f"<ul>{''.join(li_metrics)}</ul>")
                continue

        # 4. Blockquotes especiais
        if line.startswith(">"):
            b_content = line.lstrip(">").strip()
            upper_bc = b_content.upper()

            # Bloco de Analogia do Dia a Dia
            if "ANALOGIA" in upper_bc or "EM OUTRAS PALAVRAS" in upper_bc:
                clean_a = re.sub(r"^💡\s*", "", b_content)
                clean_a = re.sub(r"^\**Em outras palavras \((?:A )?Analogia\):\**\s*", "", clean_a, flags=re.IGNORECASE)
                formatted_a = format_inline(clean_a)
                html_out.append(
                    f"<div class='analogia-box'>"
                    f"<div class='analogia-header'>💡 EM OUTRAS PALAVRAS (A ANALOGIA)</div>"
                    f"<p style='margin:0;'>{formatted_a}</p>"
                    f"</div>"
                )
                linkedin_html.append(f"<blockquote>💡 <strong>Em outras palavras (A Analogia):</strong> {formatted_a}</blockquote>")
                continue

            # Pergunta prática da edição
            if "PERGUNTA PRÁTICA" in upper_bc or "A PERGUNTA PRÁTICA" in upper_bc:
                clean_p = re.sub(r"^🎯\s*", "", b_content)
                clean_p = re.sub(r"^\**A pergunta prática(?: da edição)?:\**\s*", "", clean_p, flags=re.IGNORECASE)
                formatted_p = format_inline(clean_p)
                html_out.append(
                    f"<div class='pergunta-pratica-box'>"
                    f"<div class='pergunta-pratica-header'>🎯 A PERGUNTA PRÁTICA DA EDIÇÃO</div>"
                    f"<p style='margin:0;'>{formatted_p}</p>"
                    f"</div>"
                )
                linkedin_html.append(f"<blockquote>🎯 <strong>A pergunta prática da edição:</strong> {formatted_p}</blockquote>")
                continue

            if b_content.startswith("❝") or (b_content.startswith("*") and ("—" in b_content or " - " in b_content)):
                clean_q = b_content.lstrip("❝").strip()
                if "—" in clean_q:
                    q_part, a_part = clean_q.rsplit("—", 1)
                elif " - " in clean_q:
                    q_part, a_part = clean_q.rsplit(" - ", 1)
                else:
                    q_part, a_part = clean_q, "Decifrando Dados"
                q_clean = re.sub(r"^\*+|\*+$", "", q_part.strip()).strip()
                a_clean = re.sub(r"\*\*|\*", "", a_part.strip()).strip()
                html_out.append(
                    f"<div class='quote-banner'>"
                    f"<div class='quote-text'>{html.escape(q_clean)}</div>"
                    f"<div class='quote-author'>— {html.escape(a_clean)}</div>"
                    f"</div>"
                )
                linkedin_html.append(
                    f"<blockquote>❝ <em>{html.escape(q_clean)}</em> — <strong>{html.escape(a_clean)}</strong></blockquote>"
                )
                continue

            if "💼" in b_content or "[PARCERIA]" in upper_bc or "[NA PRÁTICA]" in upper_bc:
                in_parceria = True
                parceria_lines = [b_content]
                continue

            if (
                "🎯" in b_content
                or "O TAKE PARA" in upper_bc
                or "O TAKE PRA" in upper_bc
                or "RECADO PARA" in upper_bc
                or "RECADO PRA" in upper_bc
                or "💡" in b_content
            ):
                clean_take = re.sub(r"^🎯\s*", "", b_content)
                formatted_take = format_inline(clean_take)
                html_out.append(f"<div class='take-box'>{formatted_take}</div>")
                linkedin_html.append(f"<blockquote>🎯 {formatted_take}</blockquote>")
                continue

            html_out.append(f"<div class='take-box'>{format_inline(b_content)}</div>")
            linkedin_html.append(f"<blockquote>{format_inline(b_content)}</blockquote>")
            continue

        # 5. Enquete de Encerramento
        if "CURTIU A EDIÇÃO DE HOJE" in upper_line or "CURTIU O BRIEFING DE HOJE" in upper_line:
            html_out.append(
                "<div class='poll-bar'>"
                "<span>Curtiu a edição de hoje?</span>"
                "<span class='poll-options'>Amei 😍 &nbsp;|&nbsp; Curti 😊 &nbsp;|&nbsp; Ok 😐 &nbsp;|&nbsp; Meh 🥱</span>"
                "</div>"
            )
            linkedin_html.append(
                "<hr><p><strong>Curtiu a edição de hoje?</strong> Vote nos comentários: <strong>Amei 😍 | Curti 😊 | Ok 😐 | Meh 🥱</strong></p>"
            )
            continue

        # 6. Tag de Categoria e Manchete Principal
        if line.startswith("#### ") and not main_headline_rendered:
            cat_text = line[5:].strip().upper()
            metadata["categoria"] = cat_text
            html_out.append(f"<div class='category-pill'>{html.escape(cat_text)}</div>")
            linkedin_html.append(f"<p><strong>[{html.escape(cat_text)}]</strong></p>")
            continue

        if line.startswith("# "):
            h1_text = line[2:].strip()
            if not main_headline_rendered:
                if not any("category-pill" in h for h in html_out):
                    cat_default = metadata.get("categoria", "NEGÓCIOS & IA")
                    html_out.append(f"<div class='category-pill'>{html.escape(cat_default)}</div>")
                html_out.append(f"<h1 class='main-headline'>{format_inline(h1_text)}</h1>")
                linkedin_html.append(f"<h2>{format_inline(h1_text)}</h2>")
                main_headline_rendered = True
            else:
                html_out.append(f"<h2>{format_inline(h1_text)}</h2>")
                linkedin_html.append(f"<h2>{format_inline(h1_text)}</h2>")
            continue

        if line.startswith("## "):
            h2_text = line[3:].strip()
            if h2_text == metadata.get("subtitulo"):
                continue
            html_out.append(f"<h2>{format_inline(h2_text)}</h2>")
            linkedin_html.append(f"<h2>{format_inline(h2_text)}</h2>")
            continue

        if line.startswith("### "):
            h3_text = line[4:].strip()
            html_out.append(f"<h3 class='counterpoint-sub'>{format_inline(h3_text)}</h3>")
            linkedin_html.append(f"<h3>{format_inline(h3_text)}</h3>")
            continue

        if line.startswith("#### "):
            h4_text = line[5:].strip()
            html_out.append(f"<h3 class='counterpoint-sub'>{format_inline(h4_text)}</h3>")
            linkedin_html.append(f"<h3>{format_inline(h4_text)}</h3>")
            continue

        p_formatted = format_inline(line)
        html_out.append(f"<p>{p_formatted}</p>")
        linkedin_html.append(f"<p>{p_formatted}</p>")

    flush_parceria()
    flush_section()

    article_text = generate_linkedin_article(metadata, body_md)
    return metadata, "\n".join(html_out), "\n".join(linkedin_html), article_text


def generate_linkedin_article(metadata: dict, body_md: str) -> str:
    """Gera pacote completo para publicação no LinkedIn: SEO, Post de Divulgação (Etapa 2) e Artigo Completo (Etapa 1)."""
    titulo = metadata.get("titulo", "Edição da Semana")
    subtitulo = metadata.get("subtitulo", "Smart people are cooler — Dados reais mastigados e zero corporatiquês")
    edicao = metadata.get("edicao", "01")
    assunto = metadata.get("assunto", f"⚡ {titulo}")

    seo_titulo = metadata.get("seo_titulo") or metadata.get("titulo_seo") or f"{titulo} | Decifrando Dados"
    seo_descricao = metadata.get("seo_descricao") or metadata.get("descricao_seo") or (
        f"{subtitulo[:110]} Leia na Decifrando Dados."
    )

    post_divulgacao = metadata.get("post_divulgacao") or (
        f"Na edição #{edicao} da Decifrando Dados, analisamos: {titulo}.\n\n"
        f"O que muda para Tecnologia (TI), Setor Bancário/Financeiro e Negócios.\n\n"
        f"Confira a newsletter completa no link do primeiro comentário!\n\n"
        f"#InteligenciaArtificial #CienciaDeDados #MachineLearning #Tecnologia #TI #SetorBancario #Inovacao"
    )

    clean_body = []
    for line in body_md.splitlines():
        if re.match(r"^---+$", line.strip()):
            clean_body.append("──────────────────────────────────────────────────")
            continue
        clean_body.append(line)

    package = [
        "=" * 70,
        f"DECIFRANDO DADOS (MODELO OFICIAL EM DUAS ETAPAS) - EDIÇÃO #{edicao}",
        f"ASSUNTO: {assunto}  |  SMART PEOPLE ARE COOLER.",
        "=" * 70,
        "",
        "⚙️ Metadados de SEO para o LinkedIn",
        f"Título SEO: {seo_titulo}",
        "",
        f"Descrição SEO: {seo_descricao}",
        "",
        "* Copie estes dados manualmente para a aba de configurações de SEO do seu artigo no LinkedIn.",
        "",
        "-" * 70,
        '📢 Post de Divulgação para o Feed (Etapa 2 - Leitura de 45 a 60 seg):',
        "-" * 70,
        post_divulgacao.strip(),
        "",
        "=" * 70,
        "📰 ARTIGO COMPLETO DA NEWSLETTER (ETAPA 1 - LEITURA DE 3 A 4 MIN):",
        "=" * 70,
        "",
        "[TÍTULO DO ARTIGO NO LINKEDIN]:",
        titulo,
        "",
        "[SUBTÍTULO / SLOGAN]:",
        f"{subtitulo} • Smart people are cooler.",
        "",
        "-" * 70,
        "",
        "\n".join(clean_body).strip(),
        "",
        "=" * 70,
    ]

    return "\n".join(package)


def compile_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Compila o arquivo HTML para PDF usando o Microsoft Edge headless nativo."""
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]

    edge_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_exe = p
            break

    if not edge_exe:
        print("Aviso: Microsoft Edge não encontrado nos caminhos padrão.", file=sys.stderr)
        return False

    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path.resolve()}",
        f"file:///{html_path.resolve()}",
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return pdf_path.exists()
    except Exception as e:
        print(f"Erro ao compilar PDF: {e}", file=sys.stderr)
        return False


def copy_to_clipboard(text: str) -> bool:
    """Copia o conteúdo para a área de transferência do Windows via API nativa Win32."""
    try:
        import ctypes
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        user32.OpenClipboard.argtypes = [ctypes.c_void_p]
        user32.OpenClipboard.restype = ctypes.c_int
        user32.EmptyClipboard.argtypes = []
        user32.EmptyClipboard.restype = ctypes.c_int
        user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        user32.SetClipboardData.restype = ctypes.c_void_p
        user32.CloseClipboard.argtypes = []
        user32.CloseClipboard.restype = ctypes.c_int

        kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalUnlock.restype = ctypes.c_int

        encoded = text.encode("utf-16-le") + b"\x00\x00"
        h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
        if not h_mem:
            return False
        ptr = kernel32.GlobalLock(h_mem)
        if not ptr:
            return False
        ctypes.memmove(ptr, encoded, len(encoded))
        kernel32.GlobalUnlock(h_mem)

        if not user32.OpenClipboard(None):
            return False
        user32.EmptyClipboard()
        user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        user32.CloseClipboard()
        return True
    except Exception as e:
        print(f"Erro ao copiar para clipboard: {e}", file=sys.stderr)
        return False


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Compilador da Newsletter Decifrando Dados (Modelo Oficial em Duas Etapas)")
    parser.add_argument("--input", "-i", required=True, help="Arquivo Markdown da edição")
    parser.add_argument(
        "--output-dir",
        "-o",
        default=str(OFFICIAL_EDICOES_DIR),
        help="Diretório de saída (Padrão: 01_Newsletter_Decifrando_Dados/edicoes)",
    )
    parser.add_argument("--template", "-t", default=None, help="Caminho do template HTML")
    parser.add_argument("--pdf", action="store_true", help="Gerar arquivo PDF")
    parser.add_argument("--copy", action="store_true", help="Copiar artigo do LinkedIn para a Área de Transferência")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"Erro: Arquivo não encontrado: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Garantir que sempre salve na pasta oficial C:\Users\marlo\OneDrive\Desktop\Pasta Projetos\01_Newsletter_Decifrando_Dados\edicoes
    OFFICIAL_EDICOES_DIR.mkdir(parents=True, exist_ok=True)
    output_dir = OFFICIAL_EDICOES_DIR

    template_path = Path(args.template) if args.template else Path(__file__).parent / "template.html"
    if not template_path.exists():
        print(f"Erro: Template HTML não encontrado em {template_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    metadata, body_html, linkedin_clean_html, article_linkedin = parse_markdown_to_html(md_content)

    titulo = metadata.get("titulo", "Edição")
    subtitulo = metadata.get("subtitulo", "")
    assunto = metadata.get("assunto", f"⚡ {titulo}")
    dia_semana = metadata.get("dia_semana", format_date_pt(metadata.get("data", "")))
    seo_titulo = metadata.get("seo_titulo") or metadata.get("titulo_seo") or f"{titulo} | Decifrando Dados"
    seo_descricao = metadata.get("seo_descricao") or metadata.get("descricao_seo") or (
        f"{subtitulo} Leia na Decifrando Dados."
    )
    post_divulgacao = metadata.get("post_divulgacao") or ""

    filled_html = template_html
    filled_html = filled_html.replace("{{TITULO}}", html.escape(titulo))
    filled_html = filled_html.replace("{{SUBTITULO}}", html.escape(subtitulo))
    filled_html = filled_html.replace("{{ASSUNTO}}", html.escape(assunto))
    filled_html = filled_html.replace("{{DIA_SEMANA}}", html.escape(dia_semana))
    filled_html = filled_html.replace("{{EDICAO}}", str(metadata.get("edicao", "01")))
    filled_html = filled_html.replace("{{DATA}}", metadata.get("data", datetime.now().strftime("%d/%m/%Y")))
    filled_html = filled_html.replace("{{TEMPO_LEITURA}}", str(metadata.get("tempo_leitura", "4")))
    filled_html = filled_html.replace("{{SEO_TITULO}}", html.escape(seo_titulo))
    filled_html = filled_html.replace("{{SEO_DESCRICAO}}", html.escape(seo_descricao))
    filled_html = filled_html.replace("{{POST_DIVULGACAO}}", html.escape(post_divulgacao).replace("\n", "<br>"))
    filled_html = filled_html.replace("{{RAW_POST_DIVULGACAO}}", html.escape(post_divulgacao))
    filled_html = filled_html.replace("{{CONTEUDO_HTML}}", body_html)
    filled_html = filled_html.replace("{{CONTEUDO_LINKEDIN_HTML}}", linkedin_clean_html)

    base_name = input_path.stem
    md_target = output_dir / f"{base_name}.md"
    html_output = output_dir / f"{base_name}.html"
    pdf_output = output_dir / f"{base_name}.pdf"
    article_output = output_dir / f"{base_name}_artigo_linkedin.txt"

    # Garantir que o arquivo .md também fique na pasta oficial edicoes/
    if input_path.resolve() != md_target.resolve():
        shutil.copy2(input_path, md_target)
        print(f"[OK] Markdown sincronizado em: {md_target}")

    with open(html_output, "w", encoding="utf-8") as f:
        f.write(filled_html)
    print(f"[OK] HTML Decifrando Dados gerado com sucesso: {html_output}")

    with open(article_output, "w", encoding="utf-8") as f:
        f.write(article_linkedin)
    print(f"[OK] Pacote LinkedIn em Duas Etapas pronto: {article_output}")

    if args.pdf:
        success = compile_pdf(html_output, pdf_output)
        if success:
            print(f"[OK] PDF diagramado compilado com sucesso: {pdf_output}")
        else:
            print("! Falha ao compilar PDF.", file=sys.stderr)

    if args.copy:
        if copy_to_clipboard(article_linkedin):
            print("[OK] Pacote completo do LinkedIn copiado para a Área de Transferência (Ctrl+V pronto para uso)!")


if __name__ == "__main__":
    main()
