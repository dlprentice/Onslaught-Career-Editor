/* address: 0x004238c0 */
/* name: CUnitAI__Unk_004238c0 */
/* signature: int __thiscall CUnitAI__Unk_004238c0(void * this, void * param_1, int param_2) */


int __thiscall CUnitAI__Unk_004238c0(void *this,void *param_1,int param_2)

{
  int iVar1;

  *(undefined4 *)this = 0;
  *(undefined4 *)((int)this + 8) = 0;
  iVar1 = DXMemBuffer__OpenRead(param_1,0x11,1,0);
  if (iVar1 != 0) {
    return *(int *)((int)this + 4);
  }
  return 0;
}
