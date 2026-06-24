/* address: 0x00472570 */
/* name: CGame__DoWeWantMesh */
/* signature: bool __thiscall CGame__DoWeWantMesh(void * this, int param_1, void * param_2) */


bool __thiscall CGame__DoWeWantMesh(void *this,int param_1,void *param_2)

{
  int iVar1;

  iVar1 = stricmp((char *)param_1,(char *)((int)this + 0x22c));
  if (iVar1 == 0) {
    return true;
  }
  iVar1 = stricmp((char *)param_1,(char *)((int)this + 0x25e));
  if (iVar1 == 0) {
    return true;
  }
  iVar1 = stricmp((char *)param_1,(char *)((int)this + 300));
  return (bool)('\x01' - (iVar1 != 0));
}
