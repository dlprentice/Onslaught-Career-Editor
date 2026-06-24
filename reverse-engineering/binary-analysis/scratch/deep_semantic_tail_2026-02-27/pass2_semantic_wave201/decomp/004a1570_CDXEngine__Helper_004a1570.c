/* address: 0x004a1570 */
/* name: CDXEngine__Helper_004a1570 */
/* signature: int __thiscall CDXEngine__Helper_004a1570(void * this, int param_1, void * param_2) */


int __thiscall CDXEngine__Helper_004a1570(void *this,int param_1,void *param_2)

{
  uint3 uVar1;

  uVar1 = (uint3)((uint)param_1 >> 8);
  if (((param_1 != 0) && (*(uint *)((int)this + 0x8c0) <= (uint)param_1)) &&
     ((uint)param_1 < *(uint *)((int)this + 0x8c8))) {
    *(undefined4 *)param_1 = *(undefined4 *)((int)this + 0x8c4);
    *(int *)((int)this + 0x8c4) = param_1;
    return CONCAT31(uVar1,1);
  }
  return (uint)uVar1 << 8;
}
