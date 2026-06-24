/* address: 0x0040bfd0 */
/* name: CBattleEngine__StartDieProcess */
/* signature: int __fastcall CBattleEngine__StartDieProcess(int param_1) */


int __fastcall CBattleEngine__StartDieProcess(int param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  void *this;
  int iVar3;
  void *unaff_EDI;

  if ((*(byte *)(param_1 + 0x2c) & 4) != 0) {
    return 0;
  }
  if (*(int *)(param_1 + 0x574) != 0) {
    this = CGame__GetController(&DAT_008a9a98,*(int *)(*(int *)(param_1 + 0x574) + 0x2c) + -1);
    if (this != (void *)0x0) {
      CGame__Helper_0042e750
                (this,(void *)0x0,(float)(*(int *)(*(int *)(param_1 + 0x574) + 0x2c) + -1),
                 (int)unaff_EDI);
    }
  }
  *(byte *)(param_1 + 0x2c) = *(byte *)(param_1 + 0x2c) | 4;
  CGame__DeclarePlayerDead(&DAT_008a9a98,*(int *)(*(int *)(param_1 + 0x574) + 0x2c));
  if (*(int *)(param_1 + 0x74) != 0) {
    IScript__Unk_005337e0(*(int *)(param_1 + 0x74));
    if (*(int **)(param_1 + 0x74) != (int *)0x0) {
      (**(code **)(**(int **)(param_1 + 0x74) + 4))(1);
    }
    *(undefined4 *)(param_1 + 0x74) = 0;
  }
  CGeneralVolume__Unk_0040dfb0((void *)param_1);
  iVar3 = CWorldPhysicsManager__Helper_004cd7a0
                    (&DAT_0082b400,s_Oily_Smoke_Effect_006234c8,unaff_EDI);
  CParticleManager__CreateEffect
            (iVar3,param_1 + 0x5f8,DAT_006601e8,DAT_006601ec,DAT_006601f0,DAT_006601f4,0,0);
  puVar2 = *(undefined4 **)(param_1 + 0x5fc);
  puVar1 = (undefined4 *)(param_1 + 0x1c);
  if (puVar2 != (undefined4 *)0x0) {
    if (puVar2[0x12] == 0x461c4000) {
      puVar2[0x20] = *puVar1;
      puVar2[0x21] = *(undefined4 *)(param_1 + 0x20);
      puVar2[0x22] = *(undefined4 *)(param_1 + 0x24);
      puVar2[0x23] = *(undefined4 *)(param_1 + 0x28);
      puVar2[0x10] = *puVar1;
      puVar2[0x11] = *(undefined4 *)(param_1 + 0x20);
      puVar2[0x12] = *(undefined4 *)(param_1 + 0x24);
      puVar2[0x13] = *(undefined4 *)(param_1 + 0x28);
      *puVar2 = *puVar1;
      puVar2[1] = *(undefined4 *)(param_1 + 0x20);
      puVar2[2] = *(undefined4 *)(param_1 + 0x24);
      puVar2[3] = *(undefined4 *)(param_1 + 0x28);
      if (puVar2[0x2b] != -0x40800000) {
        puVar2[0x2b] = DAT_00672fd0;
        return 1;
      }
    }
    else {
      puVar2[0x10] = *puVar2;
      puVar2[0x11] = puVar2[1];
      puVar2[0x12] = puVar2[2];
      puVar2[0x13] = puVar2[3];
      *puVar2 = *puVar1;
      puVar2[1] = *(undefined4 *)(param_1 + 0x20);
      puVar2[2] = *(undefined4 *)(param_1 + 0x24);
      puVar2[3] = *(undefined4 *)(param_1 + 0x28);
      if (puVar2[0x2b] != -0x40800000) {
        puVar2[0x2b] = DAT_00672fd0;
      }
    }
  }
  return 1;
}
