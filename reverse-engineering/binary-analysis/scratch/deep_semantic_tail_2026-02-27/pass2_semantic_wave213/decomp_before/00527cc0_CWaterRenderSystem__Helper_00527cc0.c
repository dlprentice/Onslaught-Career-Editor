/* address: 0x00527cc0 */
/* name: CWaterRenderSystem__Helper_00527cc0 */
/* signature: int __thiscall CWaterRenderSystem__Helper_00527cc0(void * this, int param_1, int param_2) */


int __thiscall CWaterRenderSystem__Helper_00527cc0(void *this,int param_1,int param_2)

{
  int extraout_EAX;

  if (*(int *)((int)this + 0xc) != param_1) {
    return param_1 & 0xffffff00;
  }
  if (*(int *)((int)this + 0x10) == 0) {
    CConsole__Printf(&DAT_0066eb90,s_RM__First_time_attempt_at___s__d_0064bc4c);
    param_1 = extraout_EAX;
  }
  return CONCAT31((int3)((uint)param_1 >> 8),1);
}
