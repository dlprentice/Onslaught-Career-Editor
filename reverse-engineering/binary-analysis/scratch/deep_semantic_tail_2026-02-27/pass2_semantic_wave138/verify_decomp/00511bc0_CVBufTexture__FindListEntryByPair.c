/* address: 0x00511bc0 */
/* name: CVBufTexture__FindListEntryByPair */
/* signature: int * __thiscall CVBufTexture__FindListEntryByPair(void * this, int param_1, int param_2, int param_3) */


int * __thiscall CVBufTexture__FindListEntryByPair(void *this,int param_1,int param_2,int param_3)

{
  undefined4 *puVar1;
  int *piVar2;

  puVar1 = *(undefined4 **)((int)this + 0x6c);
  *(undefined4 **)((int)this + 0x74) = puVar1;
  if (puVar1 == (undefined4 *)0x0) {
    piVar2 = (int *)0x0;
  }
  else {
    piVar2 = (int *)*puVar1;
  }
  while( true ) {
    if (piVar2 == (int *)0x0) {
      return (int *)0x0;
    }
    if ((piVar2[1] == param_2) && (*piVar2 == param_1)) break;
    puVar1 = *(undefined4 **)(*(int *)((int)this + 0x74) + 4);
    *(undefined4 **)((int)this + 0x74) = puVar1;
    if (puVar1 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar1;
    }
  }
  return piVar2;
}
