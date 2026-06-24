/* address: 0x00412d80 */
/* name: CGeneralVolume__HandleDashForwardInput */
/* signature: void __thiscall CGeneralVolume__HandleDashForwardInput(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CGeneralVolume__HandleDashForwardInput(void *this,int param_1,float param_2)

{
  int iVar1;
  float unaff_ESI;
  float local_44;
  float fStack_40;
  float fStack_3c;
  float fStack_38;
  undefined1 auStack_30 [4];
  float fStack_2c;
  float fStack_1c;
  float fStack_c;

  local_44 = -(*(float *)((*(int **)((int)this + 0x20))[300] + 0x10) * _DAT_005d8cc8 *
              (float)param_1);
  iVar1 = (**(code **)(**(int **)((int)this + 0x20) + 0x10c))();
  if ((iVar1 != 0) && (iVar1 = *(int *)((int)this + 0x44), iVar1 < 1)) {
    if ((-_DAT_006236b0 < *(float *)((int)this + 0x40)) &&
       (((float)param_1 < -_DAT_006236b0 && (iVar1 == 0)))) {
      *(float *)((int)this + 0x34) = DAT_00672fd0;
    }
    if ((((-_DAT_006236b4 < *(float *)((int)this + 0x40)) && ((float)param_1 < -_DAT_006236b4)) &&
        (iVar1 == 0)) &&
       ((DAT_00672fd0 - _DAT_006236ac < *(float *)((int)this + 0x38) &&
        (*(float *)((int)this + 0x38) < DAT_00672fd0 - _DAT_006236ac * _DAT_005d85ec)))) {
      CConsole__Printf(&DAT_0066f580,s_do_dash_Forward_00623910);
      CMonitor__Helper_004e1940
                (&DAT_00896988,*(void **)((int)*(void **)((int)this + 0x20) + 0x5b4),
                 *(void **)((int)this + 0x20));
      iVar1 = CGeneralVolume__ResolveCurrentOrFallbackEntry(this);
      if (iVar1 != 0) {
        *(undefined4 *)(iVar1 + 0x60) = 0;
      }
      *(undefined4 *)(*(int *)((int)this + 0x20) + 0x2ec) = 0;
      local_44 = _DAT_006236c0 * local_44;
      *(undefined4 *)((int)this + 0x44) = DAT_006236b8;
    }
    *(int *)((int)this + 0x40) = param_1;
    CSquadNormal__Helper_004062d0
              (auStack_30,*(void **)(*(int *)((int)this + 0x20) + 0x114),0.0,0.0,unaff_ESI);
    fStack_40 = fStack_2c * local_44;
    fStack_3c = fStack_1c * local_44;
    fStack_38 = fStack_c * local_44;
    if ((*(int **)((int)this + 0x20))[0x162] != 0) {
      fStack_40 = fStack_40 * _DAT_005d858c;
      fStack_3c = fStack_3c * _DAT_005d858c;
      fStack_38 = fStack_38 * _DAT_005d858c;
    }
    (**(code **)(**(int **)((int)this + 0x20) + 0x74))(&fStack_40);
  }
  return;
}
