/* address: 0x00598749 */
/* name: CTexture__HasSameFormatClassId */
/* signature: bool __thiscall CTexture__HasSameFormatClassId(void * this, int param_1, int param_2) */


bool __thiscall CTexture__HasSameFormatClassId(void *this,int param_1,int param_2)

{
  bool bVar1;

  bVar1 = false;
  if (param_1 != 0) {
    bVar1 = *(int *)(param_1 + 4) == *(int *)((int)this + 4);
  }
  return bVar1;
}
