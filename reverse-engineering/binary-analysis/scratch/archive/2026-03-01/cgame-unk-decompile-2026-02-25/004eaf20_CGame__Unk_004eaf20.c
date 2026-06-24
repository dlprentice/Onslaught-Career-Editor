/* address: 0x004eaf20 */
/* name: CGame__Unk_004eaf20 */
/* signature: int __thiscall CGame__Unk_004eaf20(void * this, int param_1, int param_2) */


int __thiscall CGame__Unk_004eaf20(void *this,int param_1,int param_2)

{
  int *this_00;
  undefined4 *puVar1;
  void *to_read;
  int iVar2;
  void *unaff_EDI;
  char *pcVar3;
  undefined1 local_14 [4];
  undefined4 *local_10;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d4ed8;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  to_read = (void *)OID__CreateObject(3,0);
  this_00 = (int *)((int)this + 0x7c);
  CGenericActiveReader__SetReader(this_00,to_read);
  if ((int *)*this_00 != (int *)0x0) {
    (**(code **)(*(int *)*this_00 + 0x24))((int)this + 0x84);
    *(undefined4 *)((int)this + 0xec) = 0;
    *(undefined4 *)((int)this + 0xf4) = 0;
    *(undefined4 *)((int)this + 0xf8) = 0;
    *(undefined4 *)((int)this + 0xfc) = 1;
    *(undefined4 *)((int)this + 0x100) = 0;
    *(undefined4 *)((int)this + 0x104) = 2;
    *(undefined4 *)((int)this + 0x108) = 2;
    *(undefined4 *)((int)this + 0x10c) = 1;
    *(undefined4 *)((int)this + 0x118) = 0xbf800000;
    *(undefined4 *)((int)this + 0xf0) = 0;
    *(undefined4 *)((int)this + 0x114) = 0;
    *(undefined4 *)((int)this + 0x110) = 0;
    *(undefined4 *)((int)this + 0x11c) = 0;
    *(undefined4 *)((int)this + 0x120) = 0;
  }
  if (param_1 != 0) {
    local_10 = (undefined4 *)0x0;
    CParticleManager__Unk_004cb040(local_14);
    uStack_4 = 0;
    if (*(int *)((int)this + 0x448) == 0) {
      pcVar3 = s_BE_Respawn_Ground_Effect_006326c0;
    }
    else {
      pcVar3 = s_BE_Respawn_Air_Effect_006326dc;
    }
    iVar2 = CParticleSet__Unk_004cd7a0(&DAT_0082b400,pcVar3,unaff_EDI);
    CParticleManager__CreateEffect
              (iVar2,local_14,DAT_0083d238,DAT_0083d23c,DAT_0083d240,DAT_0083d244,0,0);
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
        iVar2 = local_10[0x2b];
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
        iVar2 = local_10[0x2b];
      }
      if (iVar2 != -0x40800000) {
        local_10[0x2b] = DAT_00672fd0;
      }
    }
    uStack_4 = 0xffffffff;
    CParticleManager__RemoveFromGlobalList();
  }
  ExceptionList = pvStack_c;
  return *this_00;
}
