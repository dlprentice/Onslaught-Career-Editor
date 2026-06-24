/* address: 0x0044eb30 */
/* name: CFEPMultiplayerStart__Helper_0044eb30 */
/* signature: void __cdecl CFEPMultiplayerStart__Helper_0044eb30(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl CFEPMultiplayerStart__Helper_0044eb30(int param_1)

{
  byte bVar1;
  undefined4 *puVar2;
  byte *pbVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  byte *pbVar7;
  bool bVar8;

  DAT_0089da3c = DAT_0089da34;
  if (DAT_0089da34 == (undefined4 *)0x0) {
    piVar5 = (int *)0x0;
  }
  else {
    piVar5 = (int *)*DAT_0089da34;
  }
  while (piVar5 != (int *)0x0) {
    if (DAT_0089d94c == *piVar5) {
      if (piVar5 != (int *)0x0) {
        puVar2 = (undefined4 *)piVar5[5];
        iVar6 = 0;
        piVar5[7] = (int)puVar2;
        if (puVar2 == (undefined4 *)0x0) {
          puVar2 = (undefined4 *)0x0;
        }
        else {
          puVar2 = (undefined4 *)*puVar2;
        }
        if (puVar2 != (undefined4 *)0x0) goto LAB_0044eb9c;
      }
      break;
    }
    DAT_0089da3c = (undefined4 *)DAT_0089da3c[1];
    if (DAT_0089da3c == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*DAT_0089da3c;
    }
  }
  goto switchD_0044ec6a_default;
LAB_0044eb9c:
  while (iVar6 != param_1) {
    iVar6 = iVar6 + 1;
    puVar2 = *(undefined4 **)(piVar5[7] + 4);
    piVar5[7] = (int)puVar2;
    if (puVar2 == (undefined4 *)0x0) {
      puVar2 = (undefined4 *)0x0;
    }
    else {
      puVar2 = (undefined4 *)*puVar2;
    }
    if (puVar2 == (undefined4 *)0x0) {
      Text__AsciiToWideScratch(s_Unknown_Configuration_00628ea8);
      return;
    }
  }
  if ((byte *)*puVar2 != (byte *)0x0) {
    _DAT_006602a8 = DAT_006602a0;
    if (DAT_006602a0 == (int *)0x0) {
      iVar6 = 0;
    }
    else {
      iVar6 = *DAT_006602a0;
    }
    if (iVar6 != 0) {
      do {
        pbVar3 = *(byte **)(iVar6 + 0xa8);
        pbVar7 = (byte *)*puVar2;
        do {
          bVar1 = *pbVar3;
          bVar8 = bVar1 < *pbVar7;
          if (bVar1 != *pbVar7) {
LAB_0044ec1d:
            iVar4 = (1 - (uint)bVar8) - (uint)(bVar8 != 0);
            goto LAB_0044ec22;
          }
          if (bVar1 == 0) break;
          bVar1 = pbVar3[1];
          bVar8 = bVar1 < pbVar7[1];
          if (bVar1 != pbVar7[1]) goto LAB_0044ec1d;
          pbVar3 = pbVar3 + 2;
          pbVar7 = pbVar7 + 2;
        } while (bVar1 != 0);
        iVar4 = 0;
LAB_0044ec22:
        if (iVar4 == 0) {
          if (iVar6 != 0) {
            switch(*(undefined4 *)(iVar6 + 0xa4)) {
            case 1:
              CText__GetStringById(&g_Text,-0x682b8295);
              return;
            case 2:
              CText__GetStringById(&g_Text,-0x1c034084);
              return;
            case 3:
              CText__GetStringById(&g_Text,0x3025018d);
              return;
            case 4:
              CText__GetStringById(&g_Text,0x7c4d439e);
              return;
            case 5:
              CText__GetStringById(&g_Text,-0x378a7a51);
              return;
            }
          }
          break;
        }
        _DAT_006602a8 = (int *)_DAT_006602a8[1];
        if (_DAT_006602a8 == (int *)0x0) {
          iVar6 = 0;
        }
        else {
          iVar6 = *_DAT_006602a8;
        }
        if (iVar6 == 0) {
          Text__AsciiToWideScratch(s_Unknown_Configuration_00628ea8);
          return;
        }
      } while( true );
    }
  }
switchD_0044ec6a_default:
  Text__AsciiToWideScratch(s_Unknown_Configuration_00628ea8);
  return;
}
