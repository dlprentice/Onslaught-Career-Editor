/* address: 0x005078f0 */
/* name: CMonitor__Unk_005078f0 */
/* signature: void __thiscall CMonitor__Unk_005078f0(void * this, int param_1, int param_2) */


void __thiscall CMonitor__Unk_005078f0(void *this,int param_1,int param_2)

{
  undefined4 *extraout_EAX;
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  void *unaff_ESI;
  undefined4 *puVar5;
  undefined4 *puVar6;
  undefined4 *local_e4;
  undefined4 local_dc;
  undefined4 uStack_d8;
  undefined4 uStack_d4;
  undefined4 uStack_d0;
  void *pvStack_cc;
  int local_c8;
  float fStack_c4;
  undefined4 auStack_c0 [12];
  undefined1 local_90 [48];
  undefined4 auStack_60 [12];
  undefined1 auStack_30 [48];

  local_c8 = *(int *)((int)this + 0xa0);
  if (local_c8 != 0) {
    local_e4 = (undefined4 *)((int)this + 0x24);
    iVar4 = 0;
    piVar3 = (int *)((int)this + 0x18);
    do {
      if (*piVar3 != 0) {
        (**(code **)(**(int **)((int)this + 8) + 300))(this,*local_e4,&local_dc,local_90,0);
        puVar6 = (undefined4 *)*piVar3;
        if (puVar6 != (undefined4 *)0x0) {
          if (puVar6[0x12] == 0x461c4000) {
            puVar6[0x20] = local_dc;
            puVar6[0x21] = uStack_d8;
            puVar6[0x22] = uStack_d4;
            puVar6[0x23] = uStack_d0;
            puVar6[0x10] = local_dc;
            puVar6[0x11] = uStack_d8;
            puVar6[0x12] = uStack_d4;
            puVar6[0x13] = uStack_d0;
          }
          else {
            puVar6[0x10] = *puVar6;
            puVar6[0x11] = puVar6[1];
            puVar6[0x12] = puVar6[2];
            puVar6[0x13] = puVar6[3];
          }
          CMeshRenderer__Helper_00403650(puVar6,&local_dc,unaff_ESI);
        }
        if (param_1 != 0) {
          iVar2 = 0;
          puVar6 = *(undefined4 **)(local_c8 + 0x5c);
          if (puVar6 == (undefined4 *)0x0) {
            puVar5 = (undefined4 *)0x0;
          }
          else {
            puVar5 = (undefined4 *)*puVar6;
          }
          while (puVar5 != (undefined4 *)0x0) {
            if (iVar2 == iVar4) goto LAB_00507a07;
            puVar6 = (undefined4 *)puVar6[1];
            iVar2 = iVar2 + 1;
            if (puVar6 == (undefined4 *)0x0) {
              puVar5 = (undefined4 *)0x0;
            }
            else {
              puVar5 = (undefined4 *)*puVar6;
            }
          }
          puVar5 = (undefined4 *)0x0;
LAB_00507a07:
          CActor__Helper_004f8140(auStack_c0,(void *)0x0,1,0,(int)unaff_ESI);
          if (puVar5 != (undefined4 *)0x0) {
            fStack_c4 = (float)puVar5[1];
            pvStack_cc = (void *)*puVar5;
            CSquadNormal__Helper_004062d0(auStack_60,pvStack_cc,fStack_c4,0.0,(float)unaff_ESI);
            puVar6 = auStack_60;
            puVar5 = auStack_c0;
            for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
              *puVar5 = *puVar6;
              puVar6 = puVar6 + 1;
              puVar5 = puVar5 + 1;
            }
          }
          CMCBuggy__Helper_0040d320(local_90,auStack_30,auStack_c0,unaff_ESI);
          iVar2 = *piVar3;
          if (iVar2 != 0) {
            puVar6 = extraout_EAX;
            puVar5 = (undefined4 *)(iVar2 + 0x10);
            for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
              *puVar5 = *puVar6;
              puVar6 = puVar6 + 1;
              puVar5 = puVar5 + 1;
            }
            *(undefined4 *)(iVar2 + 0xa0) = 1;
          }
        }
      }
      iVar4 = iVar4 + 1;
      local_e4 = local_e4 + 1;
      piVar3 = piVar3 + 2;
    } while (iVar4 < 2);
  }
  return;
}
