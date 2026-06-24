/* address: 0x004b0cd0 */
/* name: CMesh__SelectModeSpecificPtr */
/* signature: void * __thiscall CMesh__SelectModeSpecificPtr(void * this) */


void * __thiscall CMesh__SelectModeSpecificPtr(void *this)

{
  int iVar1;

  iVar1 = *(int *)((int)this + 0x8c);
  if ((iVar1 != 1) && (iVar1 != 3)) {
    if (iVar1 == 6) {
      return *(void **)((int)this + 0x124);
    }
    this = (void *)0x0;
  }
  return this;
}
