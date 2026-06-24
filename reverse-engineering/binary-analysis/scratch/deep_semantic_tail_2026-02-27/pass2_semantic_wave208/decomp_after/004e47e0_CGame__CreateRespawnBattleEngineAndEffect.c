/* address: 0x004e47e0 */
/* name: CGame__CreateRespawnBattleEngineAndEffect */
/* signature: int * __thiscall CGame__CreateRespawnBattleEngineAndEffect(void * this, int param_1, int param_2) */


int * __thiscall CGame__CreateRespawnBattleEngineAndEffect(void *this,int param_1,int param_2)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  void *unaff_EDI;
  char *pcVar4;
  undefined1 local_14 [4];
  undefined4 *local_10;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d4cb8;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  piVar2 = (int *)OID__CreateObject(3,0);
  if (piVar2 != (int *)0x0) {
    (**(code **)(*piVar2 + 0x24))((int)this + 0x80);
    *(undefined4 *)((int)this + 0xe8) = 0;
    *(undefined4 *)((int)this + 0xf0) = 0;
    *(undefined4 *)((int)this + 0xf4) = 0;
    *(undefined4 *)((int)this + 0xf8) = 1;
    *(undefined4 *)((int)this + 0xfc) = 0;
    *(undefined4 *)((int)this + 0x100) = 2;
    *(undefined4 *)((int)this + 0x104) = 2;
    *(undefined4 *)((int)this + 0x108) = 1;
    *(undefined4 *)((int)this + 0x114) = 0xbf800000;
    *(undefined4 *)((int)this + 0xec) = 0;
    *(undefined4 *)((int)this + 0x110) = 0;
    *(undefined4 *)((int)this + 0x10c) = 0;
    *(undefined4 *)((int)this + 0x118) = 0;
    *(undefined4 *)((int)this + 0x11c) = 0;
  }
  if (param_1 != 0) {
    local_10 = (undefined4 *)0x0;
    CWorldPhysicsManager__Helper_004cb040(local_14);
    uStack_4 = 0;
    if (*(int *)((int)this + 0x444) == 0) {
      pcVar4 = s_BE_Respawn_Ground_Effect_006326c0;
    }
    else {
      pcVar4 = s_BE_Respawn_Air_Effect_006326dc;
    }
    iVar3 = CWorldPhysicsManager__Helper_004cd7a0(&DAT_0082b400,pcVar4,unaff_EDI);
    CParticleManager__CreateEffect
              (iVar3,local_14,DAT_0083d0a0,DAT_0083d0a4,DAT_0083d0a8,DAT_0083d0ac,0,0);
    puVar1 = (undefined4 *)((int)this + 0x1c);
    if (local_10 != (undefined4 *)0x0) {
      if (local_10[0x12] == 0x461c4000) {
        local_10[0x20] = *puVar1;
        local_10[0x21] = *(undefined4 *)((int)this + 0x20);
        local_10[0x22] = *(undefined4 *)((int)this + 0x24);
        local_10[0x23] = *(undefined4 *)((int)this + 0x28);
        local_10[0x10] = local_10[0x20];
        local_10[0x11] = local_10[0x21];
        local_10[0x12] = local_10[0x22];
        local_10[0x13] = local_10[0x23];
        *local_10 = *puVar1;
        local_10[1] = *(undefined4 *)((int)this + 0x20);
        local_10[2] = *(undefined4 *)((int)this + 0x24);
        local_10[3] = *(undefined4 *)((int)this + 0x28);
        iVar3 = local_10[0x2b];
      }
      else {
        local_10[0x10] = *local_10;
        local_10[0x11] = local_10[1];
        local_10[0x12] = local_10[2];
        local_10[0x13] = local_10[3];
        *local_10 = *puVar1;
        local_10[1] = *(undefined4 *)((int)this + 0x20);
        local_10[2] = *(undefined4 *)((int)this + 0x24);
        local_10[3] = *(undefined4 *)((int)this + 0x28);
        iVar3 = local_10[0x2b];
      }
      if (iVar3 != -0x40800000) {
        local_10[0x2b] = DAT_00672fd0;
      }
    }
    uStack_4 = 0xffffffff;
    CParticleManager__RemoveFromGlobalList();
  }
  ExceptionList = pvStack_c;
  return piVar2;
}
