public class Test extends Object
{
    static {
        Class c = Object[].class;
        Object s = new Object() {
            public void touchMe() {
                Object t = new Object() {
                    public void touchMe() {
                    }
                };
                Object t2 = new Object() {
                    public void touchMe() {
                    }
                };
            }
        };
        Object s2 = new Object() {
            public void touchMe() {
                Object t = new Object() {
                    public void touchMe() {
                    }
                };
                Object t2 = new Object() {
                    public void touchMe() {
                    }
                };
            }
        };
    }

    public class Inner1 extends Object
    {
        public void touchMe() {
            Class c = Object[].class;
            Object s = new Object() {
                public void touchMe() {
                    Object t = new Object() {
                        public void touchMe() {
                        }
                    };
                    Object t2 = new Object() {
                        public void touchMe() {
                        }
                    };
                }
            };
            Object s2 = new Object() {
                public void touchMe() {
                    Object t = new Object() {
                        public void touchMe() {
                        }
                    };
                    Object t2 = new Object() {
                        public void touchMe() {
                        }
                    };
                }
            };
        }

        public class Inner2 extends Object
        {
            public void touchMe() {
                Class c = Object[].class;
                Object s = new Object() {
                    public void touchMe() {
                        Object t = new Object() {
                            public void touchMe() {
                            }
                        };
                        Object t2 = new Object() {
                            public void touchMe() {
                            }
                        };
                    }
                };
                Object s2 = new Object() {
                    public void touchMe() {
                        Object t = new Object() {
                            public void touchMe() {
                            }
                        };
                        Object t2 = new Object() {
                            public void touchMe() {
                            }
                        };
                    }
                };
            }

        }

        public void touchMe2() {
            Class c = Object[].class;
            Object s = new Object() {
                public void touchMe() {
                    Object t = new Object() {
                        public void touchMe() {
                        }
                    };
                    Object t2 = new Object() {
                        public void touchMe() {
                        }
                    };
                }
            };
            Object s2 = new Object() {
                public void touchMe() {
                    Object t = new Object() {
                        public void touchMe() {
                        }
                    };
                    Object t2 = new Object() {
                        public void touchMe() {
                        }
                    };
                }
            };
        }
    }

    public void touchMe() {
        Class c = Object[].class;
        Object s = new Object() {
            public void touchMe() {
                Object t = new Object() {
                    public void touchMe() {
                    }
                };
                Object t2 = new Object() {
                    public void touchMe() {
                    }
                };
            }
        };
        Object s2 = new Object() {
            public void touchMe() {
                Object t = new Object() {
                    public void touchMe() {
                    }
                };
                Object t2 = new Object() {
                    public void touchMe() {
                    }
                };
            }
        };
    }

}
