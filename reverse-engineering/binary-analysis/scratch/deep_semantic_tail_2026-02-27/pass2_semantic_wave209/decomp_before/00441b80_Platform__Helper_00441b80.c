/* address: 0x00441b80 */
/* name: Platform__Helper_00441b80 */
/* signature: void Platform__Helper_00441b80(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void Platform__Helper_00441b80(void)

{
  int iVar1;
  int extraout_EAX;
  int extraout_EAX_00;
  int extraout_EAX_01;
  void *pvVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  int *piStack_148;
  int iStack_144;
  undefined4 uStack_140;
  undefined1 *puStack_118;
  undefined1 local_108 [4];
  char local_104 [260];

  if (DAT_0066ff74 != '\0') {
    puStack_118 = DAT_0066ff78;
    sprintf(local_104,s__s_04d_dds_00628554);
    puStack_118 = local_108;
    pvVar2 = (void *)(-(uint)(DAT_0066eb84 != -1) & 0x66eb80);
    iVar1 = (**(code **)(*DAT_00888a50 + 0x48))();
    if (iVar1 < 0) {
      CConsole__Printf(&DAT_0066eb90,s_Screen_dump__Couldn_t_get_back_b_00628528);
      return;
    }
    if (DAT_0066ff75 == '\0') {
      uStack_140 = 0x441c18;
      Platform__Helper_00574645(&puStack_118,(void *)0x4,(void *)0x0,(void *)0x0,pvVar2);
      iVar1 = extraout_EAX;
    }
    else {
      sprintf((char *)&puStack_118,s__s_04d_bmp_0062851c);
      uStack_140 = 0x441c54;
      Platform__Helper_00574645(&puStack_118,(void *)0x0,(void *)0x0,(void *)0x0,pvVar2);
      iVar1 = extraout_EAX_00;
    }
    if (iVar1 < 0) {
      CConsole__Printf(&DAT_0066eb90,s_Screen_dump__Couldn_t_save_raw_s_006284f0);
      return;
    }
    if (DAT_0066ff75 == '\0') {
      uStack_140 = 1;
      iStack_144 = 0x100;
      piStack_148 = (int *)0x100;
      iVar1 = (**(code **)(*DAT_00888a50 + 0x5c))(DAT_00888a50);
      if ((iVar1 < 0) &&
         (iVar1 = (**(code **)(*DAT_00888a50 + 0x5c))
                            (DAT_00888a50,0x80,0x80,1,0,0x17,2,&piStack_148,0), iVar1 < 0)) {
        CConsole__Printf(&DAT_0066eb90,s_Screen_dump__Couldn_t_write__s_006284d0);
        return;
      }
      piVar5 = &iStack_144;
      piVar4 = (int *)0x0;
      piVar3 = piStack_148;
      iVar1 = (**(code **)(*piStack_148 + 0x48))();
      if (iVar1 < 0) {
        CConsole__Printf(&DAT_0066eb90,s_Screen_dump__Couldn_t_get_surfac_006284a4);
        (**(code **)(*piVar4 + 8))(piVar4);
        return;
      }
      iVar1 = Platform__Helper_0057511b();
      if (iVar1 < 0) {
        CConsole__Printf(&DAT_0066eb90,s_Screen_dump__Couldn_t_reload__s_00628484);
        (**(code **)(*piVar5 + 8))(piVar5);
        (**(code **)(*piVar3 + 8))(piVar3);
        return;
      }
      Platform__Helper_00574645(&piStack_148,(void *)0x4,piVar5,(void *)0x0,(void *)0x0);
      if (extraout_EAX_01 < 0) {
        CConsole__Printf(&DAT_0066eb90,s_Screen_dump__Couldn_t_save_small_00628454);
        (**(code **)(*piVar5 + 8))(piVar5);
        (**(code **)(*piVar3 + 8))(piVar3);
        return;
      }
      (**(code **)(*piVar5 + 8))(piVar5);
      (**(code **)(*piVar3 + 8))(piVar3);
    }
    CConsole__Printf(&DAT_0066eb90,s_Screen_dump__saved__s__fullsize__00628430);
    DAT_0066ff78 = DAT_0066ff78 + 1;
    DAT_0066ff74 = '\0';
  }
  return;
}
