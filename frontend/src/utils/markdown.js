import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false
})

export function renderMarkdown(text) {
  if (!text) return ''
  try {
    return md.render(String(text))
  } catch (e) {
    return String(text)
  }
}

export default md
