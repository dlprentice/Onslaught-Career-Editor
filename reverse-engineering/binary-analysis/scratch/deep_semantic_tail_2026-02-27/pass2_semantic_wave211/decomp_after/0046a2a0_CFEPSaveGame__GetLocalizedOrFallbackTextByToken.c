/* address: 0x0046a2a0 */
/* name: CFEPSaveGame__GetLocalizedOrFallbackTextByToken */
/* signature: short * __cdecl CFEPSaveGame__GetLocalizedOrFallbackTextByToken(int param_1) */


short * __cdecl CFEPSaveGame__GetLocalizedOrFallbackTextByToken(int param_1)

{
  uchar uVar1;
  undefined3 extraout_var;
  short *extraout_EAX;
  short *extraout_EAX_00;
  short *extraout_EAX_01;
  short *extraout_EAX_02;
  short *extraout_EAX_03;
  short *extraout_EAX_04;
  short *extraout_EAX_05;
  short *extraout_EAX_06;
  short *extraout_EAX_07;
  wchar_t *pwVar2;
  short *psVar3;

  uVar1 = PlatformInput__ConsumeKeyOnce(0x2d);
  if (CONCAT31(extraout_var,uVar1) != 0) {
    DAT_00679b88 = DAT_00679b88 ^ 1;
  }
  if (DAT_00679b88 == 0) {
    switch(param_1) {
    case 0:
      psVar3 = CText__GetStringById(&g_Text,0xe39ad3);
      return psVar3;
    case 1:
      psVar3 = CText__GetStringById(&g_Text,0x1b749178);
      return psVar3;
    case 2:
      psVar3 = CText__GetStringById(&g_Text,0x1be0271);
      return psVar3;
    case 3:
      psVar3 = CText__GetStringById(&g_Text,0x1c0573d);
      return psVar3;
    case 4:
      psVar3 = CText__GetStringById(&g_Text,0x794b06e);
      return psVar3;
    case 5:
      psVar3 = CText__GetStringById(&g_Text,0x7c113d);
      return psVar3;
    case 6:
      psVar3 = CText__GetStringById(&g_Text,0x8251dc);
      return psVar3;
    case 7:
      psVar3 = CText__GetStringById(&g_Text,0xddb483);
      return psVar3;
    case 8:
      psVar3 = CText__GetStringById(&g_Text,0x141d4a);
      return psVar3;
    case 9:
      psVar3 = CText__GetStringById(&g_Text,0x3810b66);
      return psVar3;
    case 10:
      psVar3 = CText__GetStringById(&g_Text,0xe89f10a);
      return psVar3;
    case 0xb:
      psVar3 = CText__GetStringById(&g_Text,-0x1f20f458);
      return psVar3;
    case 0xc:
      psVar3 = CText__GetStringById(&g_Text,0xc93b6c);
      return psVar3;
    case 0xd:
      psVar3 = CText__GetStringById(&g_Text,0x179592a);
      return psVar3;
    case 0xe:
      psVar3 = CText__GetStringById(&g_Text,0x5cb1c2e);
      return psVar3;
    case 0xf:
      psVar3 = CText__GetStringById(&g_Text,0x5ce98381);
      return psVar3;
    case 0x10:
      psVar3 = CText__GetStringById(&g_Text,0x5c9867ea);
      return psVar3;
    case 0x11:
      psVar3 = CText__GetStringById(&g_Text,0x17b722a);
      return psVar3;
    case 0x12:
      psVar3 = CText__GetStringById(&g_Text,0xbb59d5e);
      return psVar3;
    case 0x13:
      psVar3 = CText__GetStringById(&g_Text,0xd88af9c);
      return psVar3;
    case 0x14:
      psVar3 = CText__GetStringById(&g_Text,0x1c01706);
      return psVar3;
    case 0x15:
      psVar3 = CText__GetStringById(&g_Text,0xc67e11b);
      return psVar3;
    case 0x16:
      psVar3 = CText__GetStringById(&g_Text,0x3dc6176c);
      return psVar3;
    case 0x17:
      psVar3 = CText__GetStringById(&g_Text,0x7b5590f);
      return psVar3;
    case 0x18:
      psVar3 = CText__GetStringById(&g_Text,0x1b85584);
      return psVar3;
    case 0x19:
      psVar3 = CText__GetStringById(&g_Text,0x2e88f0b);
      return psVar3;
    case 0x1a:
      psVar3 = CText__GetStringById(&g_Text,0x39ad2b5);
      return psVar3;
    case 0x1b:
      psVar3 = CText__GetStringById(&g_Text,0xbb52f);
      return psVar3;
    case 0x1c:
      psVar3 = CText__GetStringById(&g_Text,0x74cd9);
      return psVar3;
    case 0x1d:
      psVar3 = CText__GetStringById(&g_Text,0x737e5);
      return psVar3;
    case 0x1e:
      psVar3 = CText__GetStringById(&g_Text,0xe0383f6);
      return psVar3;
    case 0x1f:
      psVar3 = CText__GetStringById(&g_Text,0x1b8903f7);
      return psVar3;
    case 0x20:
      psVar3 = CText__GetStringById(&g_Text,-0x33d6d258);
      return psVar3;
    case 0x21:
      psVar3 = CText__GetStringById(&g_Text,0x7b9d24ca);
      return psVar3;
    case 0x22:
      psVar3 = CText__GetStringById(&g_Text,0x1d0a54f);
      return psVar3;
    case 0x23:
      psVar3 = CText__GetStringById(&g_Text,0x305e20a);
      return psVar3;
    case 0x24:
      psVar3 = CText__GetStringById(&g_Text,0xe69771);
      return psVar3;
    case 0x25:
      psVar3 = CText__GetStringById(&g_Text,0x1beb77bc);
      return psVar3;
    case 0x26:
      psVar3 = CText__GetStringById(&g_Text,0x1f77e31);
      return psVar3;
    case 0x27:
      psVar3 = CText__GetStringById(&g_Text,0x6d370c03);
      return psVar3;
    case 0x28:
      psVar3 = CText__GetStringById(&g_Text,0xe056cb5);
      return psVar3;
    case 0x29:
      psVar3 = CText__GetStringById(&g_Text,-0x27d4fff3);
      return psVar3;
    case 0x2a:
      psVar3 = CText__GetStringById(&g_Text,0x44337e32);
      return psVar3;
    case 0x2b:
      CFEPSaveGame__GetAsciiFallbackTextByToken(0x2b);
      return extraout_EAX_00;
    case 0x2c:
      psVar3 = CText__GetStringById(&g_Text,0x3d2e5a43);
      return psVar3;
    case 0x2d:
      psVar3 = CText__GetStringById(&g_Text,0x4031715);
      return psVar3;
    case 0x2e:
      psVar3 = CText__GetStringById(&g_Text,0x4035271);
      return psVar3;
    case 0x2f:
      psVar3 = CText__GetStringById(&g_Text,0x403441b);
      return psVar3;
    case 0x30:
      psVar3 = CText__GetStringById(&g_Text,0x4037f78);
      return psVar3;
    case 0x31:
      psVar3 = CText__GetStringById(&g_Text,0x4037121);
      return psVar3;
    case 0x32:
      psVar3 = CText__GetStringById(&g_Text,0x403ac7f);
      return psVar3;
    case 0x33:
      psVar3 = CText__GetStringById(&g_Text,0x4039e27);
      return psVar3;
    case 0x34:
      psVar3 = CText__GetStringById(&g_Text,0x403d986);
      return psVar3;
    case 0x35:
      psVar3 = CText__GetStringById(&g_Text,0x3b7e680f);
      return psVar3;
    case 0x36:
      psVar3 = CText__GetStringById(&g_Text,0x6ed8509a);
      return psVar3;
    case 0x37:
      psVar3 = CText__GetStringById(&g_Text,-0x7e4b73f8);
      return psVar3;
    case 0x38:
      psVar3 = CText__GetStringById(&g_Text,0xe4fff2);
      return psVar3;
    case 0x39:
      psVar3 = CText__GetStringById(&g_Text,0x1f4f905);
      return psVar3;
    case 0x3a:
      psVar3 = CText__GetStringById(&g_Text,0x7f9cec4);
      return psVar3;
    case 0x3b:
      psVar3 = CText__GetStringById(&g_Text,0xff5f0a1);
      return psVar3;
    case 0x3c:
      psVar3 = CText__GetStringById(&g_Text,-0xef6335);
      return psVar3;
    case 0x3d:
      psVar3 = CText__GetStringById(&g_Text,-0x15e78d4);
      return psVar3;
    case 0x3e:
      psVar3 = CText__GetStringById(&g_Text,0x7faf69be);
      return psVar3;
    case 0x3f:
      psVar3 = CText__GetStringById(&g_Text,0x3fb6c79a);
      return psVar3;
    case 0x40:
      psVar3 = CText__GetStringById(&g_Text,0x1ff32de5);
      return psVar3;
    case 0x41:
      psVar3 = CText__GetStringById(&g_Text,-0x225ecee);
      return psVar3;
    case 0x42:
      psVar3 = CText__GetStringById(&g_Text,-0x1f16ade9);
      return psVar3;
    default:
      psVar3 = Text__AsciiToWideScratch(s_Unknown_Text_0062aafc);
      return psVar3;
    case 0x45:
      psVar3 = CText__GetStringById(&g_Text,0xbdbae81);
      return psVar3;
    case 0x46:
      psVar3 = CText__GetStringById(&g_Text,-0x6fd6eeb);
      return psVar3;
    case 0x47:
      psVar3 = CText__GetStringById(&g_Text,0xc0cb2d3);
      return psVar3;
    case 0x48:
      psVar3 = CText__GetStringById(&g_Text,0xc2534fc);
      return psVar3;
    case 0x49:
      psVar3 = CText__GetStringById(&g_Text,-0x6b3ca43);
      return psVar3;
    case 0x4a:
      psVar3 = CText__GetStringById(&g_Text,-0x69b3e0b);
      return psVar3;
    case 0x4b:
      psVar3 = CText__GetStringById(&g_Text,0xdeb663);
      return psVar3;
    case 0x4c:
      psVar3 = CText__GetStringById(&g_Text,0xd6f2991);
      return psVar3;
    case 0x4d:
      psVar3 = CText__GetStringById(&g_Text,0xf9d375);
      return psVar3;
    case 0x4e:
      psVar3 = CText__GetStringById(&g_Text,0x72e4531);
      return psVar3;
    case 0x4f:
      psVar3 = CText__GetStringById(&g_Text,0x76a80c2);
      return psVar3;
    case 0x50:
      psVar3 = CText__GetStringById(&g_Text,0x3e46441);
      return psVar3;
    case 0x51:
      psVar3 = CText__GetStringById(&g_Text,0x3f1bb16);
      return psVar3;
    case 0x52:
      psVar3 = CText__GetStringById(&g_Text,0x77fdb9);
      return psVar3;
    case 0x53:
      psVar3 = CText__GetStringById(&g_Text,-0x41cec345);
      return psVar3;
    case 0x54:
      psVar3 = CText__GetStringById(&g_Text,0x788284aa);
      return psVar3;
    case 0x55:
      psVar3 = CText__GetStringById(&g_Text,0x752e0ac5);
      return psVar3;
    case 0x56:
      psVar3 = CText__GetStringById(&g_Text,-0x5df87a1);
      return psVar3;
    case 0x57:
      CFEPSaveGame__GetAsciiFallbackTextByToken(0x57);
      return extraout_EAX_01;
    case 0x58:
      psVar3 = CText__GetStringById(&g_Text,-0x253005e);
      return psVar3;
    case 0x59:
      psVar3 = CText__GetStringById(&g_Text,0x71acba1e);
      return psVar3;
    case 0x5a:
      psVar3 = CText__GetStringById(&g_Text,0x35926681);
      return psVar3;
    case 0x5b:
      psVar3 = CText__GetStringById(&g_Text,0x1ee4ac26);
      return psVar3;
    case 0x5c:
      CFEPSaveGame__GetAsciiFallbackTextByToken(0x5c);
      return extraout_EAX_02;
    case 0x5d:
      CFEPSaveGame__GetAsciiFallbackTextByToken(0x5d);
      return extraout_EAX_03;
    case 0x5e:
      CFEPSaveGame__GetAsciiFallbackTextByToken(0x5e);
      return extraout_EAX_04;
    case 0x5f:
      CFEPSaveGame__GetAsciiFallbackTextByToken(0x5f);
      return extraout_EAX_05;
    case 0x60:
      CFEPSaveGame__GetAsciiFallbackTextByToken(0x60);
      return extraout_EAX_06;
    case 0x61:
      CFEPSaveGame__GetAsciiFallbackTextByToken(0x61);
      return extraout_EAX_07;
    case 0x62:
      psVar3 = CText__GetStringById(&g_Text,0x74bd1790);
      return psVar3;
    case 99:
      psVar3 = CText__GetStringById(&g_Text,0x1f459b77);
      return psVar3;
    case 100:
      psVar3 = CText__GetStringById(&g_Text,0x3f9968a9);
      return psVar3;
    case 0x65:
      psVar3 = CText__GetStringById(&g_Text,0x88b6ab);
      return psVar3;
    case 0x66:
      psVar3 = CText__GetStringById(&g_Text,0x3f3384);
      return psVar3;
    case 0x67:
      psVar3 = CText__GetStringById(&g_Text,0x72eda3);
      return psVar3;
    case 0x68:
      psVar3 = CText__GetStringById(&g_Text,-0x32743b71);
      return psVar3;
    case 0x69:
      psVar3 = CText__GetStringById(&g_Text,0x2a53e6c7);
      return psVar3;
    case 0x6a:
      psVar3 = CText__GetStringById(&g_Text,0xe848ac);
      return psVar3;
    case 0x6b:
      psVar3 = CText__GetStringById(&g_Text,0x3905856);
      return psVar3;
    case 0x6c:
      psVar3 = CText__GetStringById(&g_Text,0x1f9f23);
      return psVar3;
    case 0x6d:
      psVar3 = CText__GetStringById(&g_Text,0x703c61);
      return psVar3;
    case 0x6e:
      psVar3 = CText__GetStringById(&g_Text,-0x31313163);
      return psVar3;
    case 0x6f:
    case 0x72:
      psVar3 = CText__GetStringById(&g_Text,0x7dea02c);
      return psVar3;
    case 0x70:
      psVar3 = CText__GetStringById(&g_Text,-0x2a95432c);
      return psVar3;
    case 0x71:
      psVar3 = CText__GetStringById(&g_Text,-0x11e3a33c);
      return psVar3;
    case 0x73:
      psVar3 = CText__GetStringById(&g_Text,-0x30038a96);
      return psVar3;
    case 0x74:
      psVar3 = CText__GetStringById(&g_Text,0x1fae562c);
      return psVar3;
    case 0x78:
      CText__GetStringById(&g_Text,0x1f9a8d9b);
      break;
    case 0x79:
      CText__GetStringById(&g_Text,0xfe8a00f);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x7a:
      CText__GetStringById(&g_Text,0x800ff93);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x8a:
      psVar3 = CText__GetStringById(&g_Text,-0x1a0fb317);
      return psVar3;
    case 0x8b:
      psVar3 = CText__GetStringById(&g_Text,0x38b58362);
      return psVar3;
    case 0x8c:
      psVar3 = CText__GetStringById(&g_Text,0x1cbca5cc);
      return psVar3;
    case 0x8d:
      psVar3 = CText__GetStringById(&g_Text,0x3879ed5);
      return psVar3;
    case 0x8e:
      psVar3 = CText__GetStringById(&g_Text,0x1c9b959);
      return psVar3;
    case 0x8f:
      psVar3 = CText__GetStringById(&g_Text,0x7004a61);
      return psVar3;
    case 0x90:
      CText__GetStringById(&g_Text,-0x3e73b428);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x91:
      CText__GetStringById(&g_Text,0x2eedc50b);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x92:
      psVar3 = CText__GetStringById(&g_Text,0x36578c5f);
      return psVar3;
    case 0x93:
      psVar3 = CText__GetStringById(&g_Text,0x78fb9e35);
      return psVar3;
    case 0x94:
      psVar3 = CText__GetStringById(&g_Text,0x12b09fa3);
      return psVar3;
    case 0x95:
      psVar3 = CText__GetStringById(&g_Text,-0x416112e1);
      return psVar3;
    case 0x96:
      psVar3 = CText__GetStringById(&g_Text,0x375857fb);
      return psVar3;
    case 0x97:
      if (g_UseAmericanEnglish != 0) {
        psVar3 = Text__AsciiToWideScratch(&DAT_0062adb4);
        return psVar3;
      }
      psVar3 = CText__GetStringById(&g_Text,0x2b3ade51);
      return psVar3;
    case 0x98:
      CText__GetStringById(&g_Text,0x6f01b1e);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x99:
      CText__GetStringById(&g_Text,0x3bbcfa71);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x9a:
      CText__GetStringById(&g_Text,0x3b49fdbe);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x9b:
      CText__GetStringById(&g_Text,-0x61fd7db8);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x9c:
      CText__GetStringById(&g_Text,0x679ecccf);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x9d:
      CText__GetStringById(&g_Text,0x387023f4);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x9e:
      CText__GetStringById(&g_Text,-0x543746df);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0x9f:
      CText__GetStringById(&g_Text,0x6b17107e);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0xa0:
      CText__GetStringById(&g_Text,-0x31e51e8e);
      pwVar2 = Localization__GetStringById(0xb5);
      CRT__WStrCpy(&DAT_00679b8c,pwVar2);
      return (short *)&DAT_00679b8c;
    case 0xa1:
      psVar3 = CText__GetStringById(&g_Text,0x150d048a);
      return psVar3;
    case 0xa2:
      psVar3 = CText__GetStringById(&g_Text,0x122025);
      return psVar3;
    case 0xa3:
      psVar3 = CText__GetStringById(&g_Text,0x1c5e31d5);
      return psVar3;
    case 0xa4:
      psVar3 = CText__GetStringById(&g_Text,0x7d83e320);
      return psVar3;
    case 0xa5:
      psVar3 = CText__GetStringById(&g_Text,0x696ff5d0);
      return psVar3;
    case 0xa6:
      psVar3 = CText__GetStringById(&g_Text,0x1bbb80be);
      return psVar3;
    case 0xa7:
      psVar3 = CText__GetStringById(&g_Text,-0x414f5be6);
      return psVar3;
    case 0xa8:
      psVar3 = CText__GetStringById(&g_Text,0x1e610f4f);
      return psVar3;
    case 0xa9:
      psVar3 = CText__GetStringById(&g_Text,-0xdd5a202);
      return psVar3;
    case 0xaa:
      psVar3 = CText__GetStringById(&g_Text,0x2d70116);
      return psVar3;
    case 0xab:
      psVar3 = CText__GetStringById(&g_Text,0x1d34b963);
      return psVar3;
    case 0xac:
      psVar3 = CText__GetStringById(&g_Text,0x1da92121);
      return psVar3;
    case 0xad:
      psVar3 = CText__GetStringById(&g_Text,0x399e5b8f);
      return psVar3;
    case 0xae:
      psVar3 = CText__GetStringById(&g_Text,-0x24435251);
      return psVar3;
    case 0xaf:
      psVar3 = CText__GetStringById(&g_Text,0x29745a61);
      return psVar3;
    case 0xb0:
      psVar3 = CText__GetStringById(&g_Text,0x49ec1c72);
      return psVar3;
    case 0xb1:
      psVar3 = CText__GetStringById(&g_Text,0x6a63de83);
      return psVar3;
    case 0xb2:
      psVar3 = CText__GetStringById(&g_Text,-0x75245f6c);
      return psVar3;
    case 0xb3:
      psVar3 = CText__GetStringById(&g_Text,-0x3acc1388);
      return psVar3;
    case 0xb4:
      psVar3 = CText__GetStringById(&g_Text,-0x71aeac14);
      return psVar3;
    case 0xb5:
      psVar3 = CText__GetStringById(&g_Text,-0x1ad3cb41);
      return psVar3;
    case 0xb6:
      switch(g_LanguageIndex) {
      case 1:
        Text__AsciiToWideScratch(&DAT_0062ad28);
        break;
      case 2:
        Text__AsciiToWideScratch(&DAT_0062ac90);
        break;
      case 3:
        Text__AsciiToWideScratch(&DAT_0062ab74);
        break;
      case 4:
        Text__AsciiToWideScratch(&DAT_0062ac1c);
        break;
      default:
        Text__AsciiToWideScratch(&DAT_0062ab0c);
      }
    }
    pwVar2 = Localization__GetStringById(0xb5);
    CRT__WStrCpy(&DAT_00679b8c,pwVar2);
    return (short *)&DAT_00679b8c;
  }
  CFEPSaveGame__GetAsciiFallbackTextByToken(param_1);
  return extraout_EAX;
}
