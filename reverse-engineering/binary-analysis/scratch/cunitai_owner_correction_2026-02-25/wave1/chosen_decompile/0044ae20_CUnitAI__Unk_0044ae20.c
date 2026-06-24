/* address: 0x0044ae20 */
/* name: CUnitAI__Unk_0044ae20 */
/* signature: int __thiscall CUnitAI__Unk_0044ae20(void * this, void * param_1, int param_2, void * param_3) */


int __thiscall CUnitAI__Unk_0044ae20(void *this,void *param_1,int param_2,void *param_3)

{
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d2498;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *(undefined4 *)this = 0;
  local_4 = 0;
  *(undefined2 *)((int)this + 4) = param_1._0_2_;
  CGenericActiveReader__SetReader(this,(void *)param_2);
  ExceptionList = local_c;
  return (int)this;
}
