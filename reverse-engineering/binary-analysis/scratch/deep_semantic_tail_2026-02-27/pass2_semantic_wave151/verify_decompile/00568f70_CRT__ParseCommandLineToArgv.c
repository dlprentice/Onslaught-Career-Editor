/* address: 0x00568f70 */
/* name: CRT__ParseCommandLineToArgv */
/* signature: void __cdecl CRT__ParseCommandLineToArgv(void * param_1, void * param_2, void * param_3, void * param_4, void * param_5) */


void __cdecl
CRT__ParseCommandLineToArgv(void *param_1,void *param_2,void *param_3,void *param_4,void *param_5)

{
  byte bVar1;
  bool bVar2;
  bool bVar3;
  byte *pbVar4;
  byte *pbVar5;
  uint uVar6;
  undefined4 *puVar7;

  *(undefined4 *)param_5 = 0;
  *(undefined4 *)param_4 = 1;
  if (param_2 != (void *)0x0) {
    *(void **)param_2 = param_3;
    param_2 = (void *)((int)param_2 + 4);
  }
  if (*(char *)param_1 == '\"') {
    while( true ) {
      bVar1 = *(byte *)((int)param_1 + 1);
      pbVar4 = (byte *)((int)param_1 + 1);
      if ((bVar1 == 0x22) || (bVar1 == 0)) break;
      if (((*(byte *)((int)&DAT_009d34c0 + bVar1 + 1) & 4) != 0) &&
         (*(int *)param_5 = *(int *)param_5 + 1, param_3 != (byte *)0x0)) {
        *(byte *)param_3 = *pbVar4;
        param_3 = (void *)((int)param_3 + 1);
        pbVar4 = (byte *)((int)param_1 + 2);
      }
      *(int *)param_5 = *(int *)param_5 + 1;
      param_1 = pbVar4;
      if (param_3 != (byte *)0x0) {
        *(byte *)param_3 = *pbVar4;
        param_3 = (void *)((int)param_3 + 1);
      }
    }
    *(int *)param_5 = *(int *)param_5 + 1;
    if (param_3 != (byte *)0x0) {
      *(byte *)param_3 = 0;
      param_3 = (void *)((int)param_3 + 1);
    }
    if (*pbVar4 == 0x22) {
      pbVar4 = (byte *)((int)param_1 + 2);
    }
  }
  else {
    do {
      *(int *)param_5 = *(int *)param_5 + 1;
      if (param_3 != (byte *)0x0) {
        *(byte *)param_3 = *(byte *)param_1;
        param_3 = (void *)((int)param_3 + 1);
      }
      bVar1 = *(byte *)param_1;
      pbVar4 = (byte *)((int)param_1 + 1);
      if ((*(byte *)((int)&DAT_009d34c0 + bVar1 + 1) & 4) != 0) {
        *(int *)param_5 = *(int *)param_5 + 1;
        if (param_3 != (byte *)0x0) {
          *(byte *)param_3 = *pbVar4;
          param_3 = (void *)((int)param_3 + 1);
        }
        pbVar4 = (byte *)((int)param_1 + 2);
      }
      if (bVar1 == 0x20) break;
      if (bVar1 == 0) goto LAB_0056901b;
      param_1 = pbVar4;
    } while (bVar1 != 9);
    if (bVar1 == 0) {
LAB_0056901b:
      pbVar4 = pbVar4 + -1;
    }
    else if (param_3 != (byte *)0x0) {
      *(byte *)((int)param_3 + -1) = 0;
    }
  }
  bVar2 = false;
  puVar7 = param_2;
  while (*pbVar4 != 0) {
    for (; (*pbVar4 == 0x20 || (*pbVar4 == 9)); pbVar4 = pbVar4 + 1) {
    }
    if (*pbVar4 == 0) break;
    if (puVar7 != (undefined4 *)0x0) {
      *puVar7 = param_3;
      puVar7 = puVar7 + 1;
      param_2 = puVar7;
    }
    *(int *)param_4 = *(int *)param_4 + 1;
    while( true ) {
      bVar3 = true;
      uVar6 = 0;
      for (; *pbVar4 == 0x5c; pbVar4 = pbVar4 + 1) {
        uVar6 = uVar6 + 1;
      }
      if (*pbVar4 == 0x22) {
        pbVar5 = pbVar4;
        if ((uVar6 & 1) == 0) {
          if ((!bVar2) || (pbVar5 = pbVar4 + 1, pbVar4[1] != 0x22)) {
            bVar3 = false;
            pbVar5 = pbVar4;
          }
          bVar2 = !bVar2;
          puVar7 = param_2;
        }
        uVar6 = uVar6 >> 1;
        pbVar4 = pbVar5;
      }
      for (; uVar6 != 0; uVar6 = uVar6 - 1) {
        if (param_3 != (byte *)0x0) {
          *(byte *)param_3 = 0x5c;
          param_3 = (void *)((int)param_3 + 1);
        }
        *(int *)param_5 = *(int *)param_5 + 1;
      }
      bVar1 = *pbVar4;
      if ((bVar1 == 0) || ((!bVar2 && ((bVar1 == 0x20 || (bVar1 == 9)))))) break;
      if (bVar3) {
        if (param_3 == (byte *)0x0) {
          if ((*(byte *)((int)&DAT_009d34c0 + bVar1 + 1) & 4) != 0) {
            pbVar4 = pbVar4 + 1;
            *(int *)param_5 = *(int *)param_5 + 1;
          }
        }
        else {
          if ((*(byte *)((int)&DAT_009d34c0 + bVar1 + 1) & 4) != 0) {
            *(byte *)param_3 = bVar1;
            param_3 = (void *)((int)param_3 + 1);
            pbVar4 = pbVar4 + 1;
            *(int *)param_5 = *(int *)param_5 + 1;
          }
          *(byte *)param_3 = *pbVar4;
          param_3 = (void *)((int)param_3 + 1);
        }
        *(int *)param_5 = *(int *)param_5 + 1;
      }
      pbVar4 = pbVar4 + 1;
    }
    if (param_3 != (byte *)0x0) {
      *(byte *)param_3 = 0;
      param_3 = (void *)((int)param_3 + 1);
    }
    *(int *)param_5 = *(int *)param_5 + 1;
  }
  if (puVar7 != (undefined4 *)0x0) {
    *puVar7 = 0;
  }
  *(int *)param_4 = *(int *)param_4 + 1;
  return;
}
