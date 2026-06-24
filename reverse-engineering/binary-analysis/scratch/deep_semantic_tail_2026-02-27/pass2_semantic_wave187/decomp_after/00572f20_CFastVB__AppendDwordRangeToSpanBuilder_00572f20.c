/* address: 0x00572f20 */
/* name: CFastVB__AppendDwordRangeToSpanBuilder_00572f20 */
/* signature: void __thiscall CFastVB__AppendDwordRangeToSpanBuilder_00572f20(void * this, int param_1, void * param_2, void * param_3) */


void __thiscall
CFastVB__AppendDwordRangeToSpanBuilder_00572f20(void *this,int param_1,void *param_2,void *param_3)

{
  undefined4 *puVar1;

  puVar1 = *(undefined4 **)((int)this + 8);
  for (; param_2 != puVar1; param_2 = (void *)((int)param_2 + 4)) {
    *(undefined4 *)param_1 = *(undefined4 *)param_2;
    param_1 = param_1 + 4;
  }
  *(int *)((int)this + 8) = param_1;
  return;
}
