/* address: 0x00428b50 */
/* name: CUnit__Helper_00428b50 */
/* signature: void __thiscall CUnit__Helper_00428b50(void * this, int param_1, void * param_2, int param_3) */


void __thiscall CUnit__Helper_00428b50(void *this,int param_1,void *param_2,int param_3)

{
  float10 fVar1;
  undefined1 local_40 [4];
  float fStack_3c;
  undefined1 local_30 [4];
  float fStack_2c;

  CGenericActiveReader__SetReader((void *)((int)this + 0x26c),(void *)param_1);
  *(void **)((int)this + 0x270) = param_2;
  if (param_1 != 0) {
    (**(code **)(*(int *)param_1 + 0x160))(0x14,param_2,local_40,local_30);
    fVar1 = (float10)fpatan((float10)fStack_3c,(float10)fStack_2c);
    *(float *)((int)this + 0x274) = (float)(-fVar1 - (float10)*(float *)(param_1 + 0x114));
    if ((*(uint *)(param_1 + 0x34) & 0x100000) != 0) {
      *(uint *)((int)this + 0x34) = *(uint *)((int)this + 0x34) | 0x100000;
    }
  }
  return;
}
