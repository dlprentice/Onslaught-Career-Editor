/* address: 0x00410210 */
/* name: CBattleEngine__Helper_00410210 */
/* signature: void * __thiscall CBattleEngine__Helper_00410210(void * this, void * param_1, int param_2) */


void * __thiscall CBattleEngine__Helper_00410210(void *this,void *param_1,int param_2)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d12e8;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CSPtrSet__Init(this);
  *(void **)((int)this + 0x18) = param_1;
  local_4 = 0;
  *(undefined4 *)((int)this + 0x1c) = 0;
  *(undefined4 *)((int)this + 0x10) = 0;
  *(undefined4 *)((int)this + 0x24) = 0;
  *(undefined4 *)((int)this + 0x28) = 0;
  *(undefined4 *)((int)this + 0x2c) = 0;
  *(undefined4 *)((int)this + 0x30) = 0;
  *(undefined4 *)((int)this + 0x34) = 0;
  *(undefined4 *)((int)this + 0x38) = 0xc1200000;
  *(undefined4 *)((int)this + 0x44) = 0xc1200000;
  *(undefined4 *)((int)this + 0x3c) = 0xc1200000;
  *(undefined4 *)((int)this + 0x40) = 0xc1200000;
  CSPtrSet_Remove__Wrapper_00412650(this);
  *(undefined4 *)((int)this + 0x48) = 0;
  *(undefined4 *)((int)this + 0x4c) = 0;
  *(undefined4 *)((int)this + 0x50) = 0;
  *(undefined4 *)((int)this + 0x20) = 0x3f000000;
  ExceptionList = local_c;
  return this;
}
