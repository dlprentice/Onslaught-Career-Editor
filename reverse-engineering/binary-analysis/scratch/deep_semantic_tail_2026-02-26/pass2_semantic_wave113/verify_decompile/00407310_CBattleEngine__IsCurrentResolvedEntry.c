/* address: 0x00407310 */
/* name: CBattleEngine__IsCurrentResolvedEntry */
/* signature: int __thiscall CBattleEngine__IsCurrentResolvedEntry(void * this, int param_1, int param_2) */


int __thiscall CBattleEngine__IsCurrentResolvedEntry(void *this,int param_1,int param_2)

{
  int iVar1;

  if (*(int *)((int)this + 0x260) == 3) {
    iVar1 = CBattleEngine__GetIndexedEntry(*(void **)((int)this + 0x57c));
  }
  else {
    iVar1 = CGeneralVolume__ResolveCurrentOrFallbackEntry(*(void **)((int)this + 0x578));
  }
  if ((iVar1 != 0) && (iVar1 == param_1)) {
    return 1;
  }
  return 0;
}
