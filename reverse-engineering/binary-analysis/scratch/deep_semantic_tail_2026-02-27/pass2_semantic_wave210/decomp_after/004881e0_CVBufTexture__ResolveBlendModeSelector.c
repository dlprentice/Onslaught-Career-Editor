/* address: 0x004881e0 */
/* name: CVBufTexture__ResolveBlendModeSelector */
/* signature: int __thiscall CVBufTexture__ResolveBlendModeSelector(void * this, int param_1, int param_2) */


int __thiscall CVBufTexture__ResolveBlendModeSelector(void *this,int param_1,int param_2)

{
  int iVar1;

  iVar1 = *(int *)((int)this + param_1 * 4 + 0x34);
  if (iVar1 != 0) {
    if (iVar1 == 1) {
      return 1;
    }
    if (iVar1 == 2) {
      return *(int *)((int)this + 0x4c);
    }
  }
  return 0;
}
