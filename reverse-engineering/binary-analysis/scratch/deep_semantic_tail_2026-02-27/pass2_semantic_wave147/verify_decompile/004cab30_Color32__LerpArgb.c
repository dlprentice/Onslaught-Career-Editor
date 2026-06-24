/* address: 0x004cab30 */
/* name: Color32__LerpArgb */
/* signature: int __cdecl Color32__LerpArgb(uint param_1, uint param_2, float param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl Color32__LerpArgb(uint param_1,uint param_2,float param_3)

{
  float fVar1;
  float fVar2;
  int iVar3;
  int iVar4;
  undefined8 local_8;

  fVar1 = _DAT_005d8568 - param_3;
  local_8 = (ulonglong)(param_2 >> 0x10 & 0xff);
  local_8._0_4_ =
       (int)(longlong)ROUND((float)(param_1 >> 0x10 & 0xff) * param_3 + (float)local_8 * fVar1);
  iVar3 = (int)local_8;
  local_8 = (ulonglong)(param_2 >> 0x18);
  fVar2 = (float)local_8;
  local_8 = (ulonglong)(param_1 >> 0x18);
  local_8._0_4_ = (int)(longlong)ROUND((float)local_8 * param_3 + fVar2 * fVar1);
  iVar4 = (int)local_8 * 0x100;
  local_8._0_4_ =
       (int)(longlong)
            ROUND((float)(param_1 >> 8 & 0xff) * param_3 + (float)(param_2 >> 8 & 0xff) * fVar1);
  iVar3 = (iVar3 + iVar4) * 0x100 + (int)local_8;
  local_8 = (ulonglong)(param_2 & 0xff);
  fVar2 = (float)local_8;
  local_8 = (ulonglong)(param_1 & 0xff);
  local_8._0_4_ = (int)(longlong)ROUND((float)local_8 * param_3 + fVar2 * fVar1);
  return iVar3 * 0x100 + (int)local_8;
}
