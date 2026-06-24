/* address: 0x004e2360 */
/* name: CSoundManager__Unk_004e2360 */
/* signature: void __thiscall CSoundManager__Unk_004e2360(void * this, int param_1, int param_2, void * param_3) */


void __thiscall CSoundManager__Unk_004e2360(void *this,int param_1,int param_2,void *param_3)

{
  char cVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  char *pcVar6;
  char *pcVar7;
  char *pcVar8;
  char local_100 [256];

  piVar2 = *(int **)((int)this + 0xc);
  do {
    if (piVar2 == (int *)0x0) {
LAB_004e2384:
      sprintf((char *)param_2,s__no_sound__0063261c);
      return;
    }
    if (param_1 < 1) {
      if ((piVar2 != (int *)0x0) && ((char)piVar2[2] != '\0')) {
        if (piVar2[1] < 0) {
          pcVar8 = s________s__no_channel__006325f4;
        }
        else {
          pcVar8 = s__s__Channel__d__0063260c;
        }
        sprintf((char *)param_2,pcVar8);
        sprintf(local_100,s_Volume____d___d__006325e0);
        uVar3 = 0xffffffff;
        pcVar8 = local_100;
        break;
      }
      goto LAB_004e2384;
    }
    piVar2 = (int *)piVar2[0x1d];
    param_1 = param_1 + -1;
  } while( true );
  while( true ) {
    uVar3 = uVar3 - 1;
    pcVar6 = pcVar8 + 1;
    cVar1 = *pcVar8;
    pcVar8 = pcVar6;
    if (cVar1 == '\0') break;
    pcVar6 = pcVar8;
    if (uVar3 == 0) break;
  }
  uVar3 = ~uVar3;
  iVar4 = -1;
  pcVar8 = (char *)param_2;
  do {
    pcVar7 = pcVar8;
    if (iVar4 == 0) break;
    iVar4 = iVar4 + -1;
    pcVar7 = pcVar8 + 1;
    cVar1 = *pcVar8;
    pcVar8 = pcVar7;
  } while (cVar1 != '\0');
  pcVar8 = pcVar6 + -uVar3;
  pcVar6 = pcVar7 + -1;
  for (uVar5 = uVar3 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
    *(undefined4 *)pcVar6 = *(undefined4 *)pcVar8;
    pcVar8 = pcVar8 + 4;
    pcVar6 = pcVar6 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar6 = *pcVar8;
    pcVar8 = pcVar8 + 1;
    pcVar6 = pcVar6 + 1;
  }
  iVar4 = piVar2[4];
  if (iVar4 == 0) {
    pcVar8 = s_No_tracking_006325d0;
  }
  else if (iVar4 == 1) {
    if ((int *)*piVar2 != (int *)0x0) {
      (**(code **)(*(int *)*piVar2 + 0xa4))();
      pcVar8 = s_SIP_tracking____s_006325bc;
      goto LAB_004e24e4;
    }
    pcVar8 = s_SIP_tracking___TARGET_DEAD_0063259c;
  }
  else if (iVar4 == 3) {
    if ((int *)*piVar2 != (int *)0x0) {
      (**(code **)(*(int *)*piVar2 + 0xa4))();
      pcVar8 = s_Follow_don_t_die_tracking____s_00632578;
LAB_004e24e4:
      sprintf(local_100,pcVar8);
      goto LAB_004e248f;
    }
    pcVar8 = s_Follow_don_t_die_tracking___TARG_0063254c;
  }
  else {
    if (iVar4 != 2) {
      return;
    }
    if ((int *)*piVar2 != (int *)0x0) {
      (**(code **)(*(int *)*piVar2 + 0xa4))();
      pcVar8 = s_Follow_and_die_tracking____s_0063252c;
      goto LAB_004e24e4;
    }
    pcVar8 = s_Follow_and_die_tracking___TARGET_00632504;
  }
  sprintf(local_100,pcVar8);
LAB_004e248f:
  uVar3 = 0xffffffff;
  pcVar8 = local_100;
  do {
    pcVar6 = pcVar8;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar6 = pcVar8 + 1;
    cVar1 = *pcVar8;
    pcVar8 = pcVar6;
  } while (cVar1 != '\0');
  uVar3 = ~uVar3;
  iVar4 = -1;
  do {
    pcVar8 = (char *)param_2;
    if (iVar4 == 0) break;
    iVar4 = iVar4 + -1;
    pcVar8 = (char *)(param_2 + 1);
    cVar1 = *(char *)param_2;
    param_2 = (int)pcVar8;
  } while (cVar1 != '\0');
  pcVar6 = pcVar6 + -uVar3;
  pcVar8 = pcVar8 + -1;
  for (uVar5 = uVar3 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
    *(undefined4 *)pcVar8 = *(undefined4 *)pcVar6;
    pcVar6 = pcVar6 + 4;
    pcVar8 = pcVar8 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar8 = *pcVar6;
    pcVar6 = pcVar6 + 1;
    pcVar8 = pcVar8 + 1;
  }
  return;
}
