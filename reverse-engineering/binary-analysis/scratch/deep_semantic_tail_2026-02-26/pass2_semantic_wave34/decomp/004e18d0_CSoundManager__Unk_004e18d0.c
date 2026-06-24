/* address: 0x004e18d0 */
/* name: CSoundManager__Unk_004e18d0 */
/* signature: void __thiscall CSoundManager__Unk_004e18d0(void * this, int param_1, int param_2, int param_3, float param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CSoundManager__Unk_004e18d0(void *this,int param_1,int param_2,int param_3,float param_4)

{
  float fVar1;
  undefined4 local_8;

  if ((*(char *)((int)this + 4) != '\0') && (param_1 != 0)) {
    fVar1 = (float)param_3 * _DAT_005d857c;
    *(int *)(param_1 + 0x3c) = param_2;
    local_8 = (undefined4)(longlong)ROUND(fVar1);
    *(undefined4 *)(param_1 + 0x40) = local_8;
  }
  return;
}
