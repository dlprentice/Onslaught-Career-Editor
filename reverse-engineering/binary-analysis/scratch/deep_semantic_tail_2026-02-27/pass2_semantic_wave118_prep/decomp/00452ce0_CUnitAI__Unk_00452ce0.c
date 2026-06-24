/* address: 0x00452ce0 */
/* name: CUnitAI__Unk_00452ce0 */
/* signature: void __stdcall CUnitAI__Unk_00452ce0(float param_1, int param_2, float param_3, float param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CUnitAI__Unk_00452ce0(float param_1,int param_2,float param_3,float param_4)

{
  int iVar1;
  float fVar2;
  undefined4 uVar3;

  if (param_3 == _DAT_005db3cc) {
    iVar1 = PLATFORM__GetWindowWidth();
    param_3 = (float)iVar1 * _DAT_005d85ec;
    iVar1 = PLATFORM__GetWindowHeight();
    param_4 = (float)iVar1 * _DAT_005d85ec;
  }
  D3DStateCache__SetStateCached(0,1,4);
  uVar3 = 1;
  iVar1 = PLATFORM__GetWindowHeight();
  fVar2 = (float)iVar1 * param_1 * _DAT_005db3c8;
  iVar1 = PLATFORM__GetWindowWidth();
  CDXFrontEndVideo__Render
            (param_3,param_4,0x3f75c28f,(float)iVar1 * param_1 * _DAT_005db3c4,fVar2,param_2,uVar3);
  return;
}
