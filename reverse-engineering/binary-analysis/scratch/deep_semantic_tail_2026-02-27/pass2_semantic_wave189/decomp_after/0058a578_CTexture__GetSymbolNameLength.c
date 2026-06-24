/* address: 0x0058a578 */
/* name: CTexture__GetSymbolNameLength */
/* signature: int __stdcall CTexture__GetSymbolNameLength(void * param_1) */


int CTexture__GetSymbolNameLength(void *param_1)

{
  if (param_1 != (void *)0x0) {
    for (; *(char *)param_1 != '\0'; param_1 = (void *)((int)param_1 + 1)) {
    }
  }
  return 0;
}
